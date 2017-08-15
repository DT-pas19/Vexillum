import os
from pathlib import Path
from typing import Optional, Dict
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog

from qt_gui.track_append_dialog import Ui_TrackDialog


class TrackAppendDialogWrapper(QtWidgets.QDialog):
    def __init__(self, MainWindow: Optional[QWidget]):
        super().__init__(MainWindow)
        self.ui = Ui_TrackDialog()
        self.ui.setupUi(self)
        self.setup_widgets()
        self.__keys__ = ('title', 'performer', 'duration', 'filename', 'max_count')

    def setup_widgets(self):
        self.ui.btn_filename.clicked.connect(self.call_open_file_dialog)

    def call_open_file_dialog(self):
        """
        Вызов диалога выбора файла
        :return:
        """
        options = QFileDialog.Options() | QFileDialog.DontResolveSymlinks

        prev_chosen_dir = self.ui.edit_filename.text()
        prev_chosen_dir = str(Path(prev_chosen_dir).parent) if os.path.exists(prev_chosen_dir) else os.getcwd()
        file_name = QFileDialog.getOpenFileName(self, "Открытие звукового файла", prev_chosen_dir, filter='*.mp3 *.flac *.ape', options=options)[0]
        if file_name:
            print("Выбран файл {}".format(file_name))
            self.ui.edit_filename.setText(file_name)

    def set_info(self, data: Dict[str, str]):
        if not isinstance(data, dict) or not any(key in data.keys() for key in self.__keys__):
            return

        def exists(key: str):
            return key in data.keys() and data.get(key, None) is not None
        if exists('title'):
            self.ui.edit_track.setText(data['title'])
        if exists('performer'):
            self.ui.edit_artist.setText(data['performer'])
        # if exists('duration'):
        #     self.ui.edit_duration.setText(data['duration'])
        if exists('filename'):
            self.ui.edit_filename.setText(data['filename'])
        if exists('max_count'):
            self.ui.box_insert_position.setMaximum(int(data['max_count']) + 1)

    def get_info(self) -> Dict[str, str]:
        data = {
            'title': self.ui.edit_track.text().strip(),
            'performer': self.ui.edit_artist.text().strip(),
            # 'duration': self.ui.edit_duration.text().strip(),
            'filename': self.ui.edit_filename.text().strip(),
            'insert_point': self.ui.box_insert_position.value(),
        }
        return data
