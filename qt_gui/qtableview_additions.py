from PyQt5.QtGui import QMouseEvent, QDropEvent
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import Qt


class ModQTableView(QTableView):
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            super().mousePressEvent(e)
        target_item = self.columnAt(e.x())
        selected_item = self.currentIndex().row()
        if target_item > -1:
            if target_item == selected_item:
                self.setDragDropMode(QAbstractItemView.InternalMove)
            else:
                self.setDragDropMode(QAbstractItemView.NoDragDrop)

    def dropEvent(self, e: QDropEvent):
        if e.source() != self:
            super().dropEvent(e)

def header_mousePressEvent(e: QMouseEvent, parent: QTableView):
    if e.button() != Qt.LeftButton:
        return
    print('Вызвано событие, текущий элемент {0}'.format(parent.currentIndex()))


def table_dropEvent(e: QDropEvent, parent: QTableView):
    if e.source() != parent:
        return
    print('Drop!')
