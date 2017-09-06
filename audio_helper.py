import multiprocessing
import os
import struct
import time
import math
from builtins import dict
from multiprocessing import Process, Queue
from multiprocessing.dummy.connection import Connection

from operator import itemgetter
from pathlib import Path
from typing import List, Tuple

import matplotlib.pylab as pylab
import numpy as np
import pyaudio
import scipy
import scipy.io.wavfile as wav
import stft
from PyQt5.QtChart import QChartView, QLineSeries, QChart
from PyQt5.QtCore import QSize, Qt, QPointF, QRectF, QTimer
from PyQt5.QtGui import QPainter, QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QPushButton, QGridLayout, QLayout, QMessageBox, QLabel
from datetime import timedelta, datetime
from pydub import AudioSegment
from pydub.utils import make_chunks

from qt_gui.spectrogram_helper import series_to_polyline

time_bit_val = 125
balanced_bit_length = ((125, 1200000), (1000, 3600000))
# сбалансированная длина отрезка при построении аудио графа (длина в мс при длительности полного аудио файла в с.)
audio_data_cache = {}


class Player:
    def __init__(self, track_path: str or Path=str()):
        self.audio_segment = AudioSegment.empty()
        self.audio_duration = 0
        self.audio_frame_rate = 0
        self.audio_path = str()
        self.audio_wave_counterpart_path = str()

        self.is_paused = True
        self.is_stopped = True
        self.play_interval = 500
        self.play_position = 0
        self.load_audio_track(track_path)
        self.command_queue = Queue()
        self.position_queue = Queue()

        self.player_process = None

        def update_position():
            data = self.receive_queue_command(self.position_queue)
            if data is not None:
                if 'position' in data:
                    self.play_position = data['position']
                    # self.position_changed(self.play_position)
                elif 'status' in data:
                    self.is_stopped = data['status'] == 'stopped'

        self.Play_position_timer = QTimer()
        self.Play_position_timer.timeout.connect(update_position)

    def load_audio_track(self, track_path: str or Path=str(), start_position: float=0):
        if self.audio_path == str(track_path):
            return
        if not self.is_stopped:
            self.stop()
        self.audio_segment = AudioSegment.empty()
        self.is_paused = True
        if os.path.exists(track_path) and os.path.isfile(track_path):
            path = Path(track_path)
            audio_format = path.suffix[1:]
            self.audio_path = str(track_path)
            self.audio_segment = AudioSegment.from_file(track_path, format=audio_format)
            self.audio_duration = len(self.audio_segment)
            self.audio_frame_rate = self.audio_segment.frame_rate

            # self.audio_wave_counterpart_path = os.path.join(tmp_dir, os.path.splitext(path.name)[0] + '.wav')
            # if not os.path.exists(self.audio_wave_counterpart_path ):
            #     self.audio_segment.export(self.audio_wave_counterpart_path, 'wav')

            self.player_process = Process(target=self.play, args=(self.audio_segment, self.command_queue, self.position_queue, start_position, self.play_interval, True))
            self.player_process.daemon = True
            self.player_process.start()
            self.play_position = 0
            self.is_stopped = False
            if not self.Play_position_timer.isActive():
                self.Play_position_timer.start(self.play_interval)
                # self.Play_position_timer.stop()

    def pause_play(self, orbitrary_pause: bool or None=None):
        self.is_paused = not self.is_paused if orbitrary_pause is None else orbitrary_pause
        self.command_queue.put(dict(pause=self.is_paused), block=False)

    def rewind(self, timestamp: timedelta):
        continue_playback = not self.is_paused
        required_stamp = timestamp.seconds * 1000 + timestamp.microseconds / 1000
        if required_stamp >= self.audio_duration:
            return
        self.command_queue.put(dict(rewind=required_stamp), block=False)
        self.play_position = required_stamp
        if continue_playback:
            self.pause_play(False)
        else:
            self.pause_play(True)

    def receive_pipe_command(self, pipe_end: Connection):
        """
        Получение команды с конца канала
        :param pipe_end: конец канала
        :return:
        """
        if pipe_end.poll(timeout=0.04):
            command = pipe_end.recv()
            return command
        return None

    def receive_queue_command(self, command_queue: Queue):
        """
        Получение команды из очереди
        :param pipe_end: конец канала
        :return:
        """
        try:
            command = command_queue.get(block=False)
        except:
            command = None
        return command

    def play(self, audio_segment: AudioSegment, command_queue: Queue, position_queue: Queue, start_position: int=0, play_interval: int=500, initial_pause: bool=False):
        """
        Воспроизведение аудио, функция предназначена для запуска в отдельном потоке
        :param audio_segment:  аудио фрагмент, Pydub.AudioSegment
        :param command_queue: очередь команд из главного потока
        :param position_queue: очередь для изменения позиции
        :param start_position: позиция в файле, с которой необходимо начать воспроизведение
        :param play_interval: длина сегмента, на которые разбивается файл при воспроизведении
        :param initial_pause: флаг запуска на паузе
        :return:
        """
        current_position = start_position
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(audio_segment.sample_width),
                        channels=audio_segment.channels,
                        rate=audio_segment.frame_rate,
                        output=True)
        pause = initial_pause
        chunks = make_chunks(audio_segment, play_interval)
        rewind = False
        first_play = True

        while rewind | first_play:
            start_fragment = int(start_position / play_interval)
            fragment_margin = start_position % play_interval
            rewind = False
            for i in range(start_fragment, len(chunks)):
                command = self.receive_queue_command(command_queue)
                while pause:
                    time.sleep(play_interval / 1000)
                    command = self.receive_queue_command(command_queue)
                    pause = command['pause'] if command is not None and 'pause' in command else pause
                    rewind = 'rewind' in command if command is not None else False
                    if rewind:
                        print('Запрошена перемотка при паузе {0}'.format(rewind))
                        break

                if command is not None:
                    pause = command['pause'] if 'pause' in command else False
                    stop = command['stop'] if 'stop' in command else False
                    rewind = 'rewind' in command  if command is not None else False
                    print('Позиция {0}, Команда \'{1}\' Пауза {2}'.format(current_position, command, pause))
                if pause:
                    continue
                if stop:
                    break
                if rewind:
                    start_position = command['rewind']
                    print('Перелистываем на позицию {0} с.'.format(start_position))
                    break
                if fragment_margin == 0:
                    stream.write(chunks[i]._data)
                else:
                    print('Начинаем не с начала 500 мс фрагмента, а с {0}'.format(fragment_margin))
                    stream.write(chunks[i][fragment_margin:]._data)
                    fragment_margin = 0
                current_position += play_interval
                position_queue.put(dict(position=current_position), block=False)
            first_play = False

        stream.stop_stream()
        stream.close()

        p.terminate()
        position_queue.put(dict(status='stopped'))
        print('About to stop')

    def play_pipe_var(self, audio_segment: AudioSegment, pipe_end: Connection, start_position: int=0, play_interval: int=500, initial_pause: bool=False):
        """
        Воспроизведение аудио, функция предназначена для запуска в отдельном потоке
        :param audio_segment:  аудио фрагмент, Pydub.AudioSegment
        :param pipe_end: конец канала, прием команд из главного потока
        :param start_position: позиция в файле, с которой необходимо начать воспроизведение
        :param play_interval: длина сегмента, на которые разбивается файл при воспроизведении
        :param initial_pause: флаг запуска на паузе
        :return:
        """
        current_position = start_position
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(audio_segment.sample_width),
                        channels=audio_segment.channels,
                        rate=audio_segment.frame_rate,
                        output=True)
        pause = initial_pause
        chunks = make_chunks(audio_segment, play_interval)
        rewind = False
        first_play = True

        while rewind | first_play:
            start_fragment = int(start_position / play_interval)
            rewind = False
            for i in range(start_fragment, len(chunks)):
                command = self.receive_pipe_command(pipe_end)
                while pause:
                    time.sleep(play_interval / 1000)
                    command = self.receive_pipe_command(pipe_end)
                    pause = command['pause'] if command is not None and 'pause' in command else pause

                print('Позиция {0}, Команда \'{1}\' Пауза {2}'.format(current_position, command, pause))
                if command is not None:
                    pause = command['pause'] if 'pause' in command else False
                    stop = command['stop'] if 'stop' in command else False
                    rewind = 'rewind' in command
                    if stop:
                        break
                    if rewind:
                        start_position = command['rewind']
                        print('Перелистываем на позицию {0} с.'.format(start_position))
                        break

                stream.write(chunks[i]._data)
                current_position += play_interval
            first_play = False

        stream.stop_stream()
        stream.close()

        p.terminate()
        self.is_stopped = True
        # self.parentEnd.send(dict(stop=True))

    def stop(self):
        self.command_queue.put(dict(stop=True), block=False)
        self.is_stopped = True
        self.Play_position_timer.stop()

    # def position_changed(self, position: int):
    #     pass


def get_audio_length(track_path: str) -> timedelta:
    """
    Returns length of an audio file
    :param track_path: path to file
    :return: length given in timedelta structure
    """
    exists = isinstance(track_path, str) and os.path.exists(track_path) and os.path.isfile(track_path)
    if not exists:
        return timedelta()
    if track_path in audio_data_cache:
        return audio_data_cache.get(audio_data_cache)
    track = AudioSegment.from_file(track_path)
    length = timedelta(milliseconds=len(track))
    audio_data_cache[audio_data_cache] = length

    return length


def get_spectrogram(wave_path: str or Path):
    # wave_path
    wave_path = str(wave_path)
    path = Path(wave_path)
    if not path.exists():
        return str()
    fs, audio = wav.read(wave_path)
    specs = stft.spectrogram(audio)

    fig = pylab.figure()
    ax = pylab.Axes(fig, [0,0,1,1])
    ax.set_axis_off()
    fig.add_axes(ax)
    pylab.imshow(scipy.absolute(specs[:][:][0].T), origin='lower', aspect='auto', interpolation='nearest')
    spectrogram_filename = os.path.join(tmp_dir, os.path.splitext(path.name)[0] + '.png')
    pylab.savefig(spectrogram_filename)

    return specs


def get_samples(audio: AudioSegment, percentage: Tuple[float, float]=(0, 100)) -> List[Tuple[int, int]]:
    print('get_the_data')
    samples = []
    audio_frames = audio.frame_count()
    start_point = int(percentage[0] * audio_frames / 100)
    end_point = int(percentage[1] * audio_frames / 100)
    audio_duration = len(audio)
    balanced_length = min(balanced_bit_length, key=lambda x: abs(audio_duration - x[1]))

    time_bit_val = math.floor(audio_duration * balanced_length[0] / balanced_length[1])
    time_bit_val = time_bit_val if time_bit_val > 50 else 50
    # в 1 мс. audio.frame_rate / 1000 кадров
    frame_interval = int(audio.frame_count(time_bit_val))
    for i in range(start_point, end_point, frame_interval):
        frame = audio.get_frame(i)
        data = struct.unpack("%ih" % 2, frame)
        samples.append(data)
    return samples


class QAudioChartView(QChartView):
    def __init__(self, parent):
        super().__init__(parent)
        self.audio_curves = 0
        self.audio_chart = QChart()
        self.audio_chart.legend().hide()
        self.setChart(self.audio_chart)
        self.chosen_file = {'file': '', 'sample': list(), 'duration': 0}
        self.channel_graphs = ()
        self.channel_curves = ()

        self.setRenderHint(QPainter.Antialiasing)
        self.setup_controls()

        self.zoom = 1
        self.play_position = 0
        self.start_playback_position = 0
        self.player = Player()
        self.render_zoom()

        update_interval = self.player.play_interval / 1000
        self.Track_bar_update_timer = QTimer()
        self.Track_bar_update_timer.timeout.connect(lambda x=update_interval*500: self.progress_track_bar_timer(x))
        self.Track_bar_update_timer.start(update_interval*500)
        # (self.progressBarPipeEnd, childEnd) = Pipe()
        # self.Track_bar_update_timer = Process(target=self.progress_track_bar, args=(childEnd, update_interval))
        # self.Track_bar_update_timer.daemon = True

        self.move_position_start = None
        self.progress_bar = None
        self.init_progress_bar()

    def setup_controls(self):
        self.layout = QGridLayout(self)
        self.layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.layout.setObjectName("layout")

        zoom_btn_side = 20
        self.btn_zoom_in = QPushButton(self)
        self.btn_zoom_in.setMaximumSize(QSize(zoom_btn_side, zoom_btn_side))
        self.btn_zoom_in.setObjectName("btn_zoom_in")
        self.btn_zoom_in.setText("+")

        self.btn_zoom_out = QPushButton(self)
        self.btn_zoom_out.setMaximumSize(QSize(zoom_btn_side, zoom_btn_side))
        self.btn_zoom_out.setObjectName("btn_zoom_out")
        self.btn_zoom_out.setText("-")

        self.btn_zoom_in.setFlat(True)
        self.btn_zoom_out.setFlat(True)

        self.lbl_zoom = QLabel(self)
        self.lbl_zoom.setMaximumSize(QSize(50, 32))
        self.lbl_zoom.setObjectName("lbl_zoom")

        self.layout.addWidget(self.btn_zoom_in, 1, 1, 1, 1, Qt.AlignRight)
        self.layout.addWidget(self.btn_zoom_out, 1, 3, 1, 1, Qt.AlignRight)
        self.layout.addWidget(self.lbl_zoom, 1, 2, 1, 1, Qt.AlignCenter)
        self.layout.setSpacing(5)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)

        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)

    # <editor-fold desc="Audio graph zoom handlers">
    def reset_zoom(self):
        if self.zoom != 1:
            self.zoom = 1
            self.render_zoom()
            self.change_zoom()

    def zoom_in(self):
        if self.zoom < 10:
            self.zoom += 0.1
            self.render_zoom()
            self.change_zoom()
            self.setFocus(Qt.MouseFocusReason)

    def zoom_out(self):
        if self.zoom > 1:
            self.zoom -= 0.1
            self.render_zoom()
            self.change_zoom()
            self.setFocus(Qt.MouseFocusReason)

    def render_zoom(self):
        desc = '{0:3}%'.format(int(self.zoom * 100))
        self.lbl_zoom.setText(desc)

    def change_zoom(self):
        if self.audio_chart.isZoomed():
            self.audio_chart.zoomReset()
        self.audio_chart.zoom(self.zoom)
    # </editor-fold>

    # <editor-fold desc="Audio graph move & rewind handlers">
    def mousePressEvent(self, e: QMouseEvent):
        print('g', end='')
        if e.button() == Qt.RightButton:
            print('m')
            self.move_position_start = (e.x(), e.y())

        if e.button() == Qt.LeftButton:
            print('r')
            audio_chart_position = self.audio_chart.mapToValue(e.pos(), next(iter(self.audio_chart.series())))
            seconds = int(audio_chart_position.x())
            ms = int((audio_chart_position.x() - seconds) * 1000)

            rewind_position = timedelta(seconds=seconds, milliseconds=ms)
            if self.player.is_stopped:
                self.start_playback_position = audio_chart_position.x()
            self.rewind(rewind_position)

    def mouseMoveEvent(self, e: QMouseEvent):
        # print('Передвигаем мышь с кнопками левая - {0}, правая {1}'.format(Qt.LeftButton == e.button(), Qt.RightButton == e.button()))
        if self.move_position_start is None:
            return
        dx = self.move_position_start[0] - e.x()
        dy = (e.y() - self.move_position_start[1])
        self.move_position_start = (e.x(), e.y())
        self.audio_chart.scroll(dx, dy)
        # TODO границы перемещения, пробел = пауза/старт, минуты на графике, пересчет длительностей при вставке timestamp

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() not in [Qt.LeftButton, Qt.RightButton]:
            return
        self.move_position_start = None
    # </editor-fold>

    def load_audio_track(self, chosen_file):
        if chosen_file == str() or self.chosen_file['file'] == chosen_file:
            return
        if not os.path.exists(chosen_file):
            print('Указанного файла не существует, сворачиваем')
            return
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Обработка звуковых данных')
        msg_box.setText('Производится обработка звуковых данных')
        msg_box.show()
        print('Начал в {0}'.format(datetime.now()))

        self.player.load_audio_track(chosen_file, self.start_playback_position)
        try:
            self.play_position = 0
            self.Track_bar_update_timer.start()
            self.position_bar_changed(self.play_position)
        except:
            pass
        self.chosen_file['file'] = chosen_file
        # samples, duration = get_samples(chosen_file)
        # self.process_audio_samples((samples, duration))

        cpu_count = multiprocessing.cpu_count()
        threads = cpu_count - 1 if cpu_count > 1 else cpu_count
        args = []
        process_width = 100 / threads

        # audio_format = Path(chosen_file).suffix[1:]
        # audio = AudioSegment.from_file(chosen_file, format=audio_format)
        audio = self.player.audio_segment
        for i in range(threads):
            ratio_arg = (i * process_width, (i + 1) * process_width)
            args.append((audio, ratio_arg))

        print('Audio has been read, starting to read samples')
        print('продолжил в {0}'.format(datetime.now()))
        with multiprocessing.Pool(processes=len(args)) as pool:
            samples = pool.starmap(get_samples, args)
            audio_data = [i for items in samples for i in items]
            self.process_audio_samples(audio_data)
            # self.sample_result = pool.starmap_async(get_samples, args, callback=self.processing_catching)
            # audio_data = get_samples(audio)
        msg_box.close()
        print('Закончил в {0}'.format(datetime.now()))
        # TODO разделять файл на несколько частей чтобы в различных потоках строить по ним графики?

    def process_audio_samples(self, audio_data: List[Tuple[int, int]]):
        if not (isinstance(audio_data, list) and all([isinstance(item, tuple) and all([isinstance(b, int) for b in item]) for item in audio_data])):
            return
        audio_len = self.player.audio_duration
        audio_frame_rate = self.player.audio_frame_rate
        self.chosen_file['sample'] = audio_data
        self.chosen_file['duration'] = audio_len

        first_channel_ydata = list(map(lambda x: x[0], audio_data))
        second_channel_ydata = list(map(lambda x: x[1] * (-1), audio_data))
        self.channel_graphs = first_channel_ydata, second_channel_ydata

        if len(self.channel_curves) > 0:
            for curve in self.channel_curves:
                 self.audio_chart.removeSeries(curve)

        xdata = np.linspace(0., audio_len / 1000, len(audio_data))
        c1 = self.add_data(xdata, first_channel_ydata, Qt.black)
        c2 = self.add_data(xdata, second_channel_ydata, Qt.darkGray)
        self.channel_curves = (c1, c2)

        min_y = min(min(first_channel_ydata), min(second_channel_ydata))
        max_y = max(max(first_channel_ydata), max(second_channel_ydata))
        self.adjust_progress_bar(min_y, max_y)
        self.adjust_zoom(audio_len, min_y, max_y)

    def pause_play_audio(self):
        if self.player.is_stopped:
            self.player.load_audio_track(self.chosen_file['file'])  # TODO перезапуск не работает
        self.player.pause_play()

    def add_data(self, xdata, ydata, color=None):
        curve = QLineSeries()
        pen = curve.pen()
        if color is not None:
            pen.setColor(color)
        pen.setWidthF(.5)
        curve.setPen(pen)
        curve.setUseOpenGL(True)
        curve.append(series_to_polyline(xdata, ydata))
        self.audio_chart.addSeries(curve)
        self.audio_chart.createDefaultAxes()
        self.audio_curves += 1
        return curve

    def init_progress_bar(self, min_y: int=-20000, max_y: int=20000):
        self.progress_bar = QLineSeries()
        pointA = QPointF(self.play_position, min_y)
        pointB = QPointF(self.play_position, max_y)
        self.progress_bar.append(pointA)
        self.progress_bar.append(pointB)
        pen = self.progress_bar.pen()
        pen.setColor(Qt.darkRed)
        pen.setWidthF(1.5)
        self.progress_bar.setPen(pen)
        self.progress_bar.setUseOpenGL(True)
        self.audio_chart.addSeries(self.progress_bar)

    def adjust_progress_bar(self, min_y: int, max_y: int):
        if min_y == 0 or max_y == 0:
            return
        bar_points = (self.progress_bar.at(0), self.progress_bar.at(1))
        heights = (min_y, max_y)
        for i in range(len(bar_points)):
            bar_points[i].setY(heights[i])
            self.progress_bar.replace(i, bar_points[i])

        changedArea = QRectF(self.play_position, min_y, self.play_position, max_y)
        self.audio_chart.plotAreaChanged.emit(changedArea)

    def adjust_zoom(self, audio_length: int, min_level: int, max_level: int):
        self.reset_zoom()
        zoom_in_area = QRectF(0, min_level, audio_length / 1000, abs(min_level) + abs(max_level))
        # self.audio_chart.zoomIn(zoom_in_area)
        axisX = self.audio_chart.axisX(self.channel_curves[0])
        axisY = self.audio_chart.axisY(self.channel_curves[0])
        axisX.setMax(audio_length / 1000)
        axisY.setRange(min_level, max_level)

    def change_position_bar(self):
        if self.progress_bar is None:
            return
        bar_points = (self.progress_bar.at(0), self.progress_bar.at(1))
        for i in range(len(bar_points)):
            bar_points[i].setX(self.play_position)
            self.progress_bar.replace(i, bar_points[i])

        changedArea = QRectF(self.play_position-10, bar_points[0].y(), self.play_position+10, bar_points[1].y())
        self.audio_chart.plotAreaChanged.emit(changedArea)

    def progress_track_bar_timer(self, update_time_msec: float=250):
        if not self.player.is_paused:
            self.play_position += update_time_msec / 1000
            # self.player.play_position / 1000
            self.change_position_bar()
            self.position_bar_changed(self.play_position)
        if self.player.is_stopped:
            self.stop_handler()
            if self.play_position != 0:
                self.play_position = 0
                self.change_position_bar()
                self.position_bar_changed(self.play_position)

    def position_bar_changed(self, position: float):
        pass

    def keyPressEvent(self, a0: QKeyEvent):
        # TODO изменяемая скорость перемотки на стрелки
        prev = self.play_position
        if a0.key() == Qt.Key_Right:
            self.play_position += 5
        if a0.key() == Qt.Key_Left:
            self.play_position -= 5
        if a0.key() == Qt.Key_Space:
            self.pause_play_audio()

        if prev != self.play_position:
            rewind_position = timedelta(seconds=self.play_position)
            self.rewind(rewind_position)
            print('Перемотка с клавишей {0} с., отныне позиция {1}'.format(self.play_position, self.player.play_position))

    def rewind(self, timestamp: timedelta):
        self.play_position = timestamp.seconds + timestamp.microseconds / 10e6
        self.player.rewind(timestamp)
        self.change_position_bar()
        self.position_bar_changed(self.play_position)

    def stop(self):
        self.player.stop()
        self.stop_handler()

    def stop_handler(self):
        pass
