# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'track_append_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TrackDialog(object):
    def setupUi(self, TrackDialog):
        TrackDialog.setObjectName("TrackDialog")
        TrackDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(TrackDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_insert_position = QtWidgets.QLabel(TrackDialog)
        self.lbl_insert_position.setObjectName("lbl_insert_position")
        self.gridLayout.addWidget(self.lbl_insert_position, 3, 0, 1, 1)
        self.edit_artist = QtWidgets.QLineEdit(TrackDialog)
        self.edit_artist.setObjectName("edit_artist")
        self.gridLayout.addWidget(self.edit_artist, 0, 1, 1, 1)
        self.lbl_track = QtWidgets.QLabel(TrackDialog)
        self.lbl_track.setObjectName("lbl_track")
        self.gridLayout.addWidget(self.lbl_track, 1, 0, 1, 1)
        self.edit_track = QtWidgets.QLineEdit(TrackDialog)
        self.edit_track.setObjectName("edit_track")
        self.gridLayout.addWidget(self.edit_track, 1, 1, 1, 1)
        self.lbl_filename = QtWidgets.QLabel(TrackDialog)
        self.lbl_filename.setObjectName("lbl_filename")
        self.gridLayout.addWidget(self.lbl_filename, 2, 0, 1, 1)
        self.box_insert_position = QtWidgets.QSpinBox(TrackDialog)
        self.box_insert_position.setMaximumSize(QtCore.QSize(80, 16777215))
        self.box_insert_position.setObjectName("box_insert_position")
        self.gridLayout.addWidget(self.box_insert_position, 3, 1, 1, 1)
        self.edit_filename = QtWidgets.QLineEdit(TrackDialog)
        self.edit_filename.setObjectName("edit_filename")
        self.gridLayout.addWidget(self.edit_filename, 2, 1, 1, 1)
        self.btn_filename = QtWidgets.QPushButton(TrackDialog)
        self.btn_filename.setMaximumSize(QtCore.QSize(30, 16777215))
        self.btn_filename.setObjectName("btn_filename")
        self.gridLayout.addWidget(self.btn_filename, 2, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(TrackDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.lbl_artist = QtWidgets.QLabel(TrackDialog)
        self.lbl_artist.setObjectName("lbl_artist")
        self.gridLayout.addWidget(self.lbl_artist, 0, 0, 1, 1)

        self.retranslateUi(TrackDialog)
        self.buttonBox.accepted.connect(TrackDialog.accept)
        self.buttonBox.rejected.connect(TrackDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TrackDialog)

    def retranslateUi(self, TrackDialog):
        _translate = QtCore.QCoreApplication.translate
        TrackDialog.setWindowTitle(_translate("TrackDialog", "Добавление композиции"))
        self.lbl_insert_position.setText(_translate("TrackDialog", "Место для вставки"))
        self.lbl_track.setText(_translate("TrackDialog", "Композиция"))
        self.lbl_filename.setText(_translate("TrackDialog", "Файл"))
        self.btn_filename.setText(_translate("TrackDialog", "..."))
        self.lbl_artist.setText(_translate("TrackDialog", "Исполнитель"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TrackDialog = QtWidgets.QDialog()
    ui = Ui_TrackDialog()
    ui.setupUi(TrackDialog)
    TrackDialog.show()
    sys.exit(app.exec_())

