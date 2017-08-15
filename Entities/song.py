from datetime import timedelta

from Entities.tag import Tag


class Song(object):
    def __init__(self, title: str, artist: str, duration: timedelta = timedelta(0), timestamp: timedelta = timedelta(0), filename: str = ""):
        self.is_same_file = filename == ""
        self.__tags__ = []
        self._duration = timedelta(0)
        self._timestamp = timedelta(0)
        self.title = title
        self.performer = artist
        self.duration = duration
        self.timestamp = timestamp
        if not self.is_same_file:
            self.filename = filename

    @property
    def title(self) -> Tag:
        title_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "title"]
        title_tag = title_tag_r[0] if title_tag_r else None
        if title_tag is None:
            return ""
        return title_tag

    @title.setter
    def title(self, name: str):
        if not(isinstance(name, str)):
            raise ValueError("Недопустимое значение названия песни")
        title_tag_r = [(index, tag) for index, tag in enumerate(self.__tags__) if tag.tag_name == "title"]
        tag_index = title_tag_r[0][0] if title_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("title", [name]))
        else:
            self.__tags__[tag_index] = Tag("title", [name])

    @property
    def performer(self) -> Tag:
        performer_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "performer"]
        performer_tag = performer_tag_r[0] if performer_tag_r else None
        if performer_tag is None:
            return ""
        return performer_tag

    @performer.setter
    def performer(self, name: str):
        if not (isinstance(name, str)):
            raise ValueError("Недопустимое значение исполнителя")
        if name == "":
            return
        performer_tag_r = [(index, tag) for index, tag in enumerate(self.__tags__) if tag.tag_name == "performer"]
        tag_index = performer_tag_r[0][0] if performer_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("performer", [name]))
        else:
            self.__tags__[tag_index] = Tag("performer", [name])

    @property
    def duration(self) -> timedelta:
        return self._duration

    @duration.setter
    def duration(self, value: timedelta):
        if not isinstance(value, timedelta):
            raise ValueError("Недопустимое значение продолжительности")
        self._duration = value

    @property
    def timestamp(self) -> timedelta:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: timedelta):
        if not isinstance(value, timedelta):
            raise ValueError("Недопустимое значение продолжительности")
        self._timestamp = value

    @property
    def filename(self) -> Tag:
        filename_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "file"]
        filename_tag = filename_tag_r[0] if filename_tag_r else None
        if filename_tag is None:
            return ''
        return filename_tag

    @filename.setter
    def filename(self, name: str):
        if not (isinstance(name, str) and name != ""):
            raise ValueError("Недопустимое значение имени файла")
        filename_tag_r = [(index, tag) for index, tag in enumerate(self.__tags__) if tag.tag_name == "file"]
        tag_index = filename_tag_r[0][0] if filename_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("file", [name, "WAVE"]))
        else:
            self.__tags__[tag_index] = Tag("file", [name, "WAVE"])

    @staticmethod
    def timespamp_str(value: timedelta):
        stamp = str(value)
        outAr = [int(p) for p in stamp.split(':')]
        outAr[1] += outAr[0]*60
        outAr = ["%02d" % x for x in outAr[1:] + [0]]
        # outAr = ["%02d" % (int(float(x))) for x in outAr]
        out = ":".join(outAr)
        return out

    def __eq__(self, other):
        if not isinstance(other, Song):
            return False
        flag = self.performer.value[0] == other.performer.value[0] if isinstance(self.performer, Tag) and isinstance(other.performer, Tag) else self.performer == other.performer
        flag = flag and self.title.value[0] == other.title.value[0]
        flag = flag and self.duration == other.duration
        return flag
