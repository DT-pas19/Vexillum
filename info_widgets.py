import tkinter as tk
import os
from tkinter.ttk import *
from typing import List, Tuple, Callable
from playlist import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from os.path import expanduser
from pathlib import Path
from parse_helper import *
from iface import Form
from parse_helper import *


class TrackFrame(Frame):
    def __init__(self, songs: List[Tuple[str, Song]]=list(), parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()

        self.file_header = None
        self.file_entries = []
        self.tracklist_vars = []

        self.init_fields(songs)
        # self.pack_forget()

    def init_fields(self, songs: List[Tuple[str, Song]]):
        for element in self.grid_slaves():
            if int(element.grid_info()["row"]) > 0:
                element.grid_forget()

        self.file_header = None
        self.file_entries = []

        self.init_vars(songs)
        self.place_widgets()

    def init_vars(self, songs: List[Tuple[str, Song]]):
        self.tracklist_vars = []
        for song in songs:
            song_vars = {
                'track': tk.StringVar(value=song[0]),
                'artist': tk.StringVar(value=song[1].performer.value[0]),
                'title': tk.StringVar(value=song[1].title.value[0]),
                'duration': tk.StringVar(value=song[1].duration),
                'filename': tk.StringVar(value=song[1].filename.value[0] if isinstance(song[1].filename, Tag) else song[1].filename)
            }
            self.tracklist_vars.append(song_vars)

    def get_data(self) -> List[Tuple[str, Song]]:
        tracklist = []
        for vars in self.tracklist_vars:
            converted = dict([(k, v.get()) for k,v in vars.items() if k != "track"])
            converted['duration'] = parse_time(converted['duration'])
            no = vars.get('track', tk.StringVar(value=0))
            song = Song(**converted)
            tracklist.append((no.get(), song))
        return tracklist

    def set_single_release_type(self):
        if self.file_header is not None:
            self.file_header.grid_remove()
            for entry in self.file_entries:
                entry.grid_remove()

    def set_multi_release_type(self):
        if self.file_header is not None:
            self.file_header.grid()
            for entry in self.file_entries:
                entry.grid()

    def place_widgets(self):
        Label(self, text='#', width=5).grid(row=0, column=0)
        Label(self, text='Artist', width=25).grid(row=0, column=1)
        Label(self, text='Title', width=35).grid(row=0, column=2)
        Label(self, text='Dur', width=10).grid(row=0, column=3)
        self.file_header = Label(self, text='File', width=15)
        self.file_header.grid(row=0, column=4)

        for i in range(len(self.tracklist_vars)):
            Entry(self, textvariable=self.tracklist_vars[i]['track'], width=5)\
                .grid(row=1+i, column=0, sticky=tk.NW)
            Entry(self, textvariable=self.tracklist_vars[i]['artist'], width=25) \
                .grid(row=1+i, column=1, sticky=tk.NW)
            Entry(self, textvariable=self.tracklist_vars[i]['title'], width=35) \
                .grid(row=1+i, column=2, sticky=tk.NW)
            Entry(self, textvariable=self.tracklist_vars[i]['duration'], width=10)\
                .grid(row=1+i, column=3, sticky=tk.NW)
            file_entry = Entry(self, textvariable=self.tracklist_vars[i]['filename'], width=15)
            file_entry.grid(row=1+i, column=4, sticky=tk.NW)
            self.file_entries.append(file_entry)
            # file_entry.grid_forget()


class CueFrame(Frame):
    # TODO tag highlight
    # http://stackoverflow.com/questions/14786507/how-to-change-the-color-of-certain-words-in-the-tkinter-text-widget
    def __init__(self, playlist: Playlist=None, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()
        self.text = None
        self.place_widgets()

        if playlist is not None:
            self.set_cue_sheet(playlist)

    def set_cue_sheet(self, playlist: Playlist):
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', str(playlist))
        self.text.mark_set(tk.INSERT, '1.0')
        self.text.focus()

    def get_data(self):
        text = self.text.get('1.0', tk.END + '-1c')
        return text

    def place_widgets(self):
        bar = Scrollbar(self)
        self.text = tk.Text(self, relief=tk.SUNKEN)
        bar.config(command=self.text.yview)
        self.text.config(yscrollcommand=bar.set)
        self.text.bind("<Control-Key-a>", lambda: Form.select_all(self.text))
        self.text.bind("<Control-Key-A>", lambda: Form.select_all(self.text))

        bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)


class FileButton(Frame):
    def __init__(self, parent=None, is_save_btn=True, connected_variable: tk.StringVar=None, misc_action: Callable[[str], None]=None, **options):
        Frame.__init__(self, parent, **options)
        self.__initial_dir__ = ""
        self.__chosen_file__ = ""

        if connected_variable is not None:
            self.initial_dir = str(Path(connected_variable.get()).parent)
        else:
            self.initial_dir = expanduser("~")

        self.pack()

        if is_save_btn:
            self.__btn__ = Button(self, text='Сохранить', width=10, command=lambda: self.save_action(connected_variable))
        else:
            self.__btn__ = Button(self, text='Открыть', width=10,
                                  command=lambda: self.open_action(connected_variable))
        self.__btn__.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

    @property
    def initial_dir(self) -> str:
        return self.__initial_dir__

    @initial_dir.setter
    def initial_dir(self, name: str or Path):
        if not (isinstance(name, str) or isinstance(name, Path)):
            raise ValueError("Недопустимое значение имени директории")
        if name == "" or not os.path.isdir(name):
            return
        self.__initial_dir__ = name

    @property
    def chosen_file(self) -> str:
        return self.__chosen_file__

    def chosen_file(self, file: str):
        if not (isinstance(file, str)):
            raise ValueError("Недопустимое значение имени файла")
        self.__chosen_file__ = file

    def open_action(self, connected_variable: tk.StringVar):
        ask = askopenfilename(initialdir=self.initial_dir,
                              title='Выбор звукового файла',
                              filetypes=(("Lossless flac", "*.flac"),
                                         ("MPEG Layer-3", "*.mp3"),
                                         ("Monkey's Audio", "*.ape"),
                                         ("All Files", "*.*"))
                              )
        if ask:
            self.chosen_file = ask
            if connected_variable is not None:
                connected_variable.set(ask)
                self.initial_dir = str(Path(ask).parent)
        print('Было передано для открытия \'{0}\''.format(ask))

    def save_action(self, connected_variable: tk.StringVar):
        ask = asksaveasfilename(initialdir=self.initial_dir,
                                defaultextension=".cue",
                                title='Сохранение cue файла',
                                filetypes=(("Cue sheet", "*.cue"),
                                           ("All Files", "*.*"))
                                )
        if ask:
            self.chosen_file = ask
            if connected_variable is not None:
                connected_variable.set(ask)
                self.initial_dir = str(Path(ask).parent)
        print('Было передано для сохранения \'{0}\''.format(ask))


class TrackTextFieldFrame(Frame):
    __patterns__ = (
        "%{artist} - %{track} %{title} - %{duration}",
        "%{artist} - %{track} %{title} - %{timestamp}",
        "%{track} %{title} - %{duration}",
        "%{track} %{title} - %{timestamp}",
        "%{track}. %{title}",
        "%{track} - %{title}")

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()
        self.text = None
        self.track_info_pattern = tk.StringVar(value="%{artist} - %{track} %{title} - %{duration}")
        self.place_widgets()

    def get_data(self, track_filename: str, general_artist: str):
        text = self.text.get('1.0', tk.END + '-1c')
        result = parse_tracks(track_filename, self.track_info_pattern.get(), text, general_artist)
        return result

    def place_widgets(self):
        upper_part = Frame(self, relief=tk.SUNKEN, height=30)
        lower_part = Frame(self, relief=tk.SUNKEN)

        Label(upper_part, text='Pattern', width=20).pack(side=tk.LEFT)
        pattern_box = Combobox(upper_part,
                               textvariable=self.track_info_pattern,
                               state='active', width=50)  # readonly
        pattern_box['values'] = self.__patterns__
        pattern_box.current(0)
        pattern_box.pack(side=tk.RIGHT, expand=tk.YES)

        upper_part.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

        bar = Scrollbar(lower_part)
        self.text = tk.Text(lower_part, relief=tk.SUNKEN)  # , variable=self.track_list)
        lower_part.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        bar.config(command=self.text.yview)
        self.text.config(yscrollcommand=bar.set)

        self.text.bind("<Control-Key-a>", lambda: Form.select_all(self.text))
        self.text.bind("<Control-Key-A>", lambda: Form.select_all(self.text))

        bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
