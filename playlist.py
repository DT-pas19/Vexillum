import datetime
from typing import List
from tag import Tag
from song import Song

indent_space_count = 2


class Playlist(object):

    def __init__(self, filename: str = "", songs: List[Song] = list(), title: str= "", performer: str = "", genre: str = "", date: int = 0, comment: str = ""):
        self.__tags__ = []
        self.filename = filename
        self.title = title
        self.performer = performer
        self.genre = genre
        self.date = date
        self.comment = comment
        self.songs = songs

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
            raise ValueError("Недопустимое значение названия альбома")
        if name == "":
            return
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
    def genre(self) -> Tag:
        genre_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "genre"]
        genre_tag = genre_tag_r[0] if genre_tag_r else None
        if genre_tag is None:
            return ""
        return genre_tag

    @genre.setter
    def genre(self, name: str):
        if not(isinstance(name, str)):
            raise ValueError("Недопустимое значение названия жанра")
        if name == "":
            return
        genre_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "genre"]
        tag_index = genre_tag_r[0][0] if genre_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("rem", ["genre", name]))
        else:
            self.__tags__[tag_index] = Tag("rem", ["genre", name])

    @property
    def date(self) -> Tag:
        date_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "date"]
        date_tag = date_tag_r[0] if date_tag_r else None
        if date_tag is None:
            return 0
        return date_tag

    @date.setter
    def date(self, value: int):
        if not (isinstance(value, int)):
            raise ValueError("Недопустимое значение даты")
        if value == 0:
            return
        date_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "date"]
        tag_index = date_tag_r[0][0] if date_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("rem", ["date", value]))
        else:
            self.__tags__[tag_index] = Tag("rem", ["date", value])

    @property
    def comment(self) -> Tag:
        # comment_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "comment"]
        comment_tag_r = list(filter(lambda x: x.iss("rem comment")), self.__tags__)
        comment_tag = comment_tag_r[0] if comment_tag_r else None
        if comment_tag is None:
            return ""
        return comment_tag

    @comment.setter
    def comment(self, value: str):
        if not(isinstance(value, str)):
            raise ValueError("Недопустимое значение комментария")
        comment_tag_r = [tag for tag in self.__tags__ if tag.tag_name == "rem" and tag.value[0].lower() == "comment"]
        tag_index = comment_tag_r[0][0] if comment_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("rem", ["comment", value]))
        else:
            self.__tags__[tag_index] = Tag("rem", ["comment", value])

    @property
    def filename(self) -> Tag:
        filename_tag_r = [tag for tag in self.__tags__ if tag.iss("file")]
        filename_tag = filename_tag_r[0] if filename_tag_r else None
        if filename_tag is None:
            return ""
        return filename_tag

    @filename.setter
    def filename(self, name: str):
        if not (isinstance(name, str)):
            raise ValueError("Недопустимое значение имени файла")
        filename_tag_r = [(index, tag) for index, tag in enumerate(self.__tags__) if tag.iss("file")]
        tag_index = filename_tag_r[0][0] if filename_tag_r else None
        if tag_index is None:
            self.__tags__.append(Tag("file", [name, "WAVE"]))
        else:
            self.__tags__[tag_index] = Tag("file", [name, "WAVE"])

    """
    def dump_data(self, List):
        with open(file=self.filename, mode="wt", encoding="utf-8") as f:
            text = f.writelines()
        return text
    #if tag_index is None:
        self.__tags__.append(Tag("index", ["01", value]))
    else:
        self.__tags__[tag_index] = Tag("index", [value])
    """

    def __str__(self):
        result = ""
        remarks = filter(lambda x: x.iss("rem"), self.__tags__)
        for tag in remarks:
            result += str(tag) + "\n"
        result += str(self.performer)+"\n" if self.performer is not None else ""
        result += str(self.title)+"\n" if self.title is not None else ""
        result += str(self.filename) + "\n" if self.filename is not None else ""

        timestamp = datetime.timedelta()
        spaces = "".join([' ' for i in range(indent_space_count)])

        for number, song in enumerate(self.songs, 1):  # TODO сохранять нумерацию из формы
            track_tag = Tag("track", ["{0:02d}".format(number), "AUDIO"])
            result += spaces + str(track_tag) + "\n"
            result += spaces * 2 + str(song.title) + "\n"
            result += spaces * 2 + str(song.performer) + "\n"

            if not song.is_same_file:
                result += spaces * 2 + str(song.filename) + "\n"

            index_tag = Tag("index", ["01", Song.timespamp_str(timestamp)])
            result += spaces * 2 + str(index_tag) + "\n"
            timestamp += song.duration

        return result
