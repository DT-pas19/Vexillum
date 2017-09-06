import os
from datetime import timedelta
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QHeaderView, QWidget

from Entities.playlist import Playlist
from parse_helper import parse_tracks, timedelta_str, parse_time
from qt_gui.track_table_model import TrackInfoModel
from qt_gui.vexillum import Ui_MainWindow


class Program(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.track_info_model = TrackInfoModel()
        self.dir_name = str()
        self.setup_widgets()

    def setup_widgets(self):
        """
        Настройка элементов формы
        :return:
        """
        self.ui.btn_filedialog.clicked.connect(self.call_open_file_dialog)

        tab_switch = lambda x: self.ui.tab_tracks.setCurrentIndex(x)
        self.ui.btn_next_1.clicked.connect(self.parse_input_data)
        self.ui.btn_next_2.clicked.connect(self.form_cue_sheets)
        self.ui.btn_prev_1.clicked.connect(lambda checked, i=0: tab_switch(i))
        self.ui.btn_prev_2.clicked.connect(lambda checked, i=1: tab_switch(i))
        self.ui.btn_save.clicked.connect(self.call_save_file_dialog)

        self.ui.box_pattern.addItems((
            "%{artist} - %{track} %{title} - %{duration}",
            "%{artist} - %{track} %{title} - %{timestamp}",
            "%{track} - %{artist} - %{title}",
            "%{track} %{title} - %{duration}",
            "%{track} %{title} - %{timestamp}",
            "%{track}. %{title}",
            "%{track} - %{title}",
            "%{track}. %{title}. %{duration}",
        ))
        self.ui.box_pattern.setCurrentIndex(7)

        self.ui.table_tracks.setModel(self.track_info_model)
        self.ui.table_tracks.setSortingEnabled(True)
        self.ui.table_tracks.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.track_info_model.add_context_menu_actions(self.ui.table_tracks)
        # self.ui.table_tracks.setAlternatingRowColors(True)
        # self.ui.table_tracks.setDropIndicatorShown(True)
        # self.ui.table_tracks.setAcceptDrops(True)
        # self.ui.table_tracks.setDragEnabled(True)
        # self.ui.table_tracks.setDragDropMode(DragDrop)

        def stop_handler():
            self.ui.btn_pause_play.setChecked(False)
            if not self.ui.visual_gram.player.is_stopped:
                self.ui.visual_gram.stop()
        self.ui.btn_stop.clicked.connect(stop_handler)
        self.ui.visual_gram.stop_handler = stop_handler
        self.ui.btn_pause_play.clicked.connect(self.ui.visual_gram.pause_play_audio)

        self.ui.edit_artist.textEdited.connect(self.track_info_model.set_performer)
        self.ui.edit_filename.editingFinished.connect(
            lambda: self.ui.visual_gram.load_audio_track(self.ui.edit_filename.text()))
        self.ui.visual_gram.position_bar_changed = self.update_timestamp
        self.ui.edit_timestamp.editingFinished.connect(self.update_position)
        self.ui.btn_paste_timestamp.clicked.connect(self.paste_position)

        self.set_tab_order()

    def set_tab_order(self):
        QWidget.setTabOrder(self.ui.edit_artist, self.ui.edit_album)
        QWidget.setTabOrder(self.ui.edit_album, self.ui.edit_date)
        QWidget.setTabOrder(self.ui.edit_date, self.ui.edit_disknumber)
        QWidget.setTabOrder(self.ui.edit_disknumber, self.ui.edit_comment)
        QWidget.setTabOrder(self.ui.edit_comment, self.ui.edit_filename)
        QWidget.setTabOrder(self.ui.edit_filename, self.ui.btn_filedialog)
        QWidget.setTabOrder(self.ui.btn_filedialog, self.ui.box_pattern)
        QWidget.setTabOrder(self.ui.box_pattern, self.ui.edit_trackdata)

    def parse_input_data(self):
        text = self.ui.edit_trackdata.toPlainText()
        general_artist = self.ui.edit_artist.text()
        track_filename = self.ui.edit_filename.text()
        pattern = self.ui.box_pattern.currentText()
        result = parse_tracks(track_filename, pattern, text, general_artist)
        songs = [song for number, song in result]
        self.track_info_model.clear()
        self.track_info_model.append(songs)
        self.ui.tab_tracks.setCurrentIndex(1)

    def form_cue_sheets(self):
        file = self.ui.edit_filename.text()
        file = file if os.path.exists(file) else ''
        songs = self.track_info_model.get_data()

        disknumber = self.ui.edit_disknumber.text()
        play = Playlist(file,
                        title=self.ui.edit_album.text(),
                        performer=self.ui.edit_artist.text(),
                        date=self.ui.edit_date.text(),
                        songs=songs,
                        comment=self.ui.edit_comment.text(),
                        discnumber=int(disknumber) if disknumber != str() and disknumber.isnumeric() else 0)
        self.ui.edit_cue_sheets.setText(str(play))
        self.ui.tab_tracks.setCurrentIndex(2)

    def call_open_file_dialog(self):
        """
        Вызов диалога выбора файла
        :return:
        """
        options = QFileDialog.Options() | QFileDialog.DontResolveSymlinks

        prev_chosen_dir = self.ui.edit_filename.text()
        prev_chosen_dir = str(Path(prev_chosen_dir).parent) if os.path.exists(prev_chosen_dir) else os.getcwd()
        file_name = QFileDialog.getOpenFileName(self, "Открытие звукового файла", prev_chosen_dir, filter='*.mp3 *.flac *.ape', options=options)[0]  # отдельное отображение - '*.mp3 ;; *.flac ;; *.ape'
        if file_name:
            print("Выбран файл {}".format(file_name))
            self.ui.edit_filename.setText(file_name)
            self.ui.visual_gram.load_audio_track(self.ui.edit_filename.text())

    def call_save_file_dialog(self):
        options = QFileDialog.Options() | QFileDialog.DontResolveSymlinks

        prev_chosen_dir = self.ui.edit_filename.text()
        prev_chosen_dir = str(Path(prev_chosen_dir).parent) if os.path.exists(prev_chosen_dir) else os.getcwd()
        file_name = QFileDialog.getSaveFileName(self, 'Сохранение результата', prev_chosen_dir, filter='*.cue', options=options)
        if file_name:
            req_file_name = next(iter(file_name))
            with open(file=req_file_name, mode="wt", encoding="utf-8") as f:
                data = self.ui.edit_cue_sheets.toPlainText()
                f.write(data)

    def update_timestamp(self, position: float):
        sec = int(position)
        ms = int((position - sec) * 1000)
        position = timedelta(seconds=sec, milliseconds=ms)
        self.ui.edit_timestamp.setText(timedelta_str(position))

    def update_position(self):
        position = parse_time(self.ui.edit_timestamp.text())
        self.ui.visual_gram.rewind(position)

    def paste_position(self):
        position = parse_time(self.ui.edit_timestamp.text())
        if len(self.ui.table_tracks.selectedIndexes()) > 0:
            edit_index = self.ui.table_tracks.currentIndex().row()
            self.track_info_model.insert_timestamp(edit_index, position)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Program()
    MainWindow.show()
    sys.exit(app.exec_())
