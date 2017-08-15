import re
from datetime import timedelta
from typing import List, Tuple, Any

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QAbstractItemModel, QMimeData
from PyQt5.QtWidgets import QTableView, QAction, QMessageBox
from namedlist import namedlist

from Entities.song import Song
from Entities.tag import Tag
from parse_helper import parse_time
from qt_gui.track_append_dialog_wrapper import TrackAppendDialogWrapper

track_info_item = namedlist('track_info_item', ['no', 'performer', 'title', 'duration'])


# TODO кнопка выбора файлов, хинты для времени, отображать на графике временные отметки композиций
class TrackInfoModel(QAbstractTableModel):
    def __init__(self):
        self.items = list()
        self.column_captions = ('Исполнитель', 'Композиция', 'Временная отметка', 'Файл', 'Длительность')
        self.column_prop_names = ('performer', 'title', 'timestamp', 'filename', 'duration')
        super(TrackInfoModel, self).__init__()

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.column_captions)

    def data(self, index=QModelIndex(), role: int = Qt.DisplayRole):
        """
        Отображение данных
        :param index: индекс - строка/колонка
        :param role: тип отображения данных
        :return:
        """
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            attr = self.column_prop_names[index.column()]
            value = getattr(self.items[index.row()], attr)
            if attr == 'duration' or attr == 'timestamp':
                return str(value)
            if isinstance(value, Tag):
                value = value.value[0]
            return QVariant('{}'.format(value))

        return QVariant()

    def flags(self, index: QModelIndex):
        default_flags = QAbstractItemModel.flags(self, index)
        if not index.isValid():
            return default_flags | Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        flags = default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        if index.column() == 4:
            return flags
        return flags | Qt.ItemIsEditable

    def supportedDropActions(self):
        return Qt.MoveAction | Qt.CopyAction | Qt.TargetMoveAction

    def headerData(self, column: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """
        Отображение заголовков
        :param column: номер колонки
        :param orientation: ориентация верт/гориз
        :param role: тип отображения данных
        :return:
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.column_captions[column])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(column+1)
        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole):
        if index.isValid() and role == Qt.EditRole:
            attr = self.column_prop_names[index.column()]
            if attr == 'duration' or attr == 'timestamp':
                value = parse_time(value)
                # components = list(map(lambda x: int(x), value.split(':')))
                # components = components[::-1]
                # if len(components) == 1:
                #     components.append(0)
                # if len(components) == 2:
                #     components.append(0)
                # seconds = components[0] + 60 * components[1] + 60*60*components[2]
                # value = timedelta(seconds=seconds)

            setattr(self.items[index.row()], attr, value)

            if attr == 'duration' or attr == 'timestamp':
                self.refresh_durations(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False

    def get_data(self) -> List[Song]:
        """
        Возвращает представление таблицы в виде массива
        :return: массив
        """
        return self.items

    def append(self, tracks: List[Tuple[Song]]):
        if not isinstance(tracks, list) or len(tracks) == 0 or not all([isinstance(f, Song) for f in tracks]):
            return
        self.items += tracks
        self.layoutChanged.emit()

    def removeRow(self, row: int, parent: QModelIndex = ...):
        if parent.isValid():
            self.items.remove(self.items[row])

    def clear(self):
        self.items = list()

    def sort(self, column: int, order: Qt.SortOrder = ...):
        # if column not in [0, 1, 4, 16]:
        #     return
        attr = self.column_prop_names[column]
        self.items = sorted(self.items, key=lambda x: getattr(x, attr).value if isinstance(getattr(x, attr), Tag) else getattr(x, attr))
        if order == Qt.DescendingOrder:
            self.items.reverse()
        self.layoutChanged.emit()

    def mimeTypes(self):
        type = 'application/songs.text.list'
        return [type]

    def mimeData(self, indexes: Any):
        mimeData = QMimeData()
        copy_info = '<table>\n'
        rows = set()
        for index in indexes:
            if index.isValid():
                rows.add(index.row())
        for row in rows:
            item = self.items[row]
            item_data = {
                'row': row,
                'performer': item.performer.value[0] if isinstance(item.performer, Tag) else str(),
                'title': item.title.value[0] if isinstance(item.title, Tag) else str(),
                'duration': str(item.duration.seconds),
                'filename': item.filename.value[0] if isinstance(item.filename, Tag) else str()
            }
            copy_info += '<tr>\n\t<td>{0[row]}</td>\n\t' \
                         '<td>{0[performer]}</td>\n\t' \
                         '<td>{0[title]}</td>\n\t' \
                         '<td>{0[duration]}</td>\n\t' \
                         '<td>{0[filename]}</td>\n</tr>\n'.format(item_data)

        copy_info += '</table>'
        print('Copied')
        mimeData.setHtml(copy_info)  # 'application/songs.text.list',
        return mimeData

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex):
        condition = data.hasHtml() and '<table>' in data.html()
        print('Можно ли вставлять? {0} = {1} & {2}\n{3}'.format(condition, data.hasHtml(), '<table>' in data.html(), data.html()))
        return condition

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False
        if action == Qt.IgnoreAction:
            return True
        if row != -1:
            insert_row_index = row
        elif parent.isValid():  # указали на существующую строку
            insert_row_index = parent.row()
        else:
            insert_row_index = len(self.items)

        result_list = []
        move_data = data.html()
        start_point = re.search('</?table>', move_data).span()[1]
        end_point = re.search('</?table>', move_data[start_point:]).span()[0]
        table_data = move_data[start_point:start_point + end_point]

        rows = re.split('</?tr>', table_data)
        rows = list(filter(lambda x: len(x) != 0 and x != '\n', rows))

        removal_indices = []
        for row in rows:
            if row.strip() == str():
                continue
            cells = re.split('</?td>', row)
            cells = list(filter(lambda x: x != '\n' and x != '\n\t', cells))

            prev_index = int(cells[0])
            performer = cells[1]
            title = cells[2]
            duration = timedelta(seconds=int(cells[3]))
            filename = cells[4]
            mime_item = Song(title, performer, duration, filename)
            # result_list.append(mime_item)
            result_list.append(self.items[prev_index])
            if insert_row_index < prev_index:
                prev_index += len(rows)
            else:
                insert_row_index += 1
            removal_indices.append(prev_index)

        items = self.items[:insert_row_index] + result_list + self.items[insert_row_index:]
        self.items = [item for i, item in enumerate(items) if i not in removal_indices]
        self.layoutChanged.emit()
        return True

    def set_performer(self, value):
        if value != str() and len(self.items) != 0:
            for item in self.items:
                 item.performer = value
            self.layoutChanged.emit()

    def add_context_menu_actions(self, parent: QTableView):
        parent.setContextMenuPolicy(Qt.ActionsContextMenu)
        move_up_action = QAction('Переместить вверх', self)
        move_down_action = QAction('Переместить вниз', self)
        append_action = QAction('Добавить', self)
        remove_action = QAction('Удалить', self)

        move_up_action.triggered.connect(lambda: self.move_action_handler(parent, -1))
        move_down_action.triggered.connect(lambda: self.move_action_handler(parent, 1))
        append_action.triggered.connect(lambda: self.append_item(parent))
        remove_action.triggered.connect(lambda: self.remove_item(parent))

        parent.addAction(move_up_action)
        parent.addAction(move_down_action)
        parent.addAction(append_action)
        parent.addAction(remove_action)

    def move_action_handler(self, parent: QTableView, delta: int):
        index = parent.currentIndex().row()
        self.move_item(index, delta)

    def move_item(self, index: int, interval: int):
        if not isinstance(index, int) or index < 0 or index > len(self.items):
            return
        if not isinstance(interval, int):
            return
        if index + interval < 0:
            interval = index
        if index + interval > len(self.items):
            interval = len(self.items) - index - 1

        itemless_list = self.items[:index] + self.items[index + 1:]
        requested_item = self.items[index]
        result = itemless_list[:index + interval] + [requested_item] + itemless_list[index + interval:]
        self.items = result
        self.layoutChanged.emit()

    def append_item(self, parent: QTableView):
        info = dict(max_count=len(self.items))
        append_dialog = TrackAppendDialogWrapper(parent)
        append_dialog.set_info(info)
        append_dialog.show()

        def accept_changes():
            result = append_dialog.get_info()
            constructed = Song(title=result['title'], artist=result['performer'], filename=result['filename'])
            insert_point = int(result['insert_point'])
            if insert_point < len(self.items):
                self.items.insert(insert_point, constructed)
            else:
                self.items.append(constructed)
            self.layoutChanged.emit()

        append_dialog.ui.buttonBox.accepted.connect(accept_changes)

    def remove_item(self, parent: QTableView):
        row = parent.currentIndex().row()
        requested_title = self.items[row].title.value[0] if isinstance(self.items[row].title, Tag) else ''
        choice = QMessageBox.question(self, 'Удаление элемента', 'Удалить \"{0}\" (#{1})'.format(requested_title, row), QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.items.remove(self.items[row])

    def insert_timestamp(self, index: int, timestamp: timedelta):
        if not isinstance(timestamp, timedelta) or timestamp.days < 0:
            return
        if not isinstance(index, int) or index < 0 or index > len(self.items):
            return
        self.items[index].timestamp = timestamp

    def refresh_durations(self, index: int):
        if not isinstance(index, int) or index < 0 or index > len(self.items):
            return
        if index < len(self.items) - 1:
            self.items[index].duration = self.items[index + 1].timestamp - self.items[index].timestamp
        else:
            diff = self.items[index - 1].duration - (self.items[index].timestamp - self.items[index - 1].timestamp)
            self.items[index].duration += diff
        self.items[index - 1].duration = self.items[index].timestamp - self.items[index - 1].timestamp
