from tkinter.messagebox import *
from tkinter.ttk import *
import tkinter as tk
import datetime
from song import Song
from parse_helper import *
from info_widgets import *
from typing import List
from playlist import *


class Form(Frame):
    __patterns__ = ("%{artist} - %{track} %{title} - %{duration}", "%{track} %{title} - %{duration}", "%{track}. %{title}", "%{track} - %{title}")

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()

        self.release_type = tk.StringVar()
        self.artist = tk.StringVar()
        self.album = tk.StringVar()
        self.date = tk.IntVar(value=0)
        self.comment = tk.StringVar()
        self.discno = tk.IntVar(value=1)
        # TODO вынести панель в класс, задействовать discno

        self.filename = tk.StringVar()
        self.track_info_pattern = tk.StringVar(value="%{artist} - %{track} %{title} - %{duration}")

        self.track_list_box = None
        self.tracks_info_frame = None
        self.tracks_table = None
        self.cue_frame = None
        self.file_frame = None
        # self.track_list = tk.StringVar()

        self.next_btn = None

        self.place_widgets()

    def change_release_type(self):
        release = self.release_type.get()
        track_frame_tab = self.tracks_info_frame.tab('1')

        if release == "single":
            if self.tracks_table is not None:
                self.tracks_table.set_single_release_type()
            #self.file_frame.state(["active"])
            self.file_frame.grid()

        if release == "multi":
            if self.tracks_table is not None:
                self.tracks_table.set_multi_release_type()
            self.file_frame.grid_remove()
            # self.file_frame.state(["disabled"])
            # TODO https://docs.python.org/3.1/library/tkinter.ttk.html#widget-states

    def place_widgets(self):
        type_frame = Frame(self)
        Label(type_frame, text='Type', width=20).pack(side=tk.LEFT)
        Radiobutton(type_frame,
                    text="One artist release",
                    variable=self.release_type,
                    value="single",
                    command=self.change_release_type).pack(side=tk.LEFT)
        Radiobutton(type_frame,
                    text="Multiple artist compilation",
                    variable=self.release_type,
                    value="multi",
                    command=self.change_release_type).pack(side=tk.LEFT)
        self.release_type.set('single')
        type_frame.pack(anchor=tk.NW, side=tk.TOP)

        release_info_frame = Frame(self)
        Label(release_info_frame, text='Artist', width=15).grid(row=0, column=0)
        Entry(release_info_frame, textvariable=self.artist, width=50).grid(row=0, column=1, sticky=tk.NW)
        Label(release_info_frame, text='Album', width=15).grid(row=1, column=0)
        Entry(release_info_frame, textvariable=self.album, width=50).grid(row=1, column=1, sticky=tk.NW)
        Label(release_info_frame, text='Date', width=15).grid(row=2, column=0)
        Entry(release_info_frame, textvariable=self.date, width=20).grid(row=2, column=1, sticky=tk.NW)
        Label(release_info_frame, text='Comment', width=15).grid(row=3, column=0)
        Entry(release_info_frame, textvariable=self.comment, width=70).grid(row=3, column=1, sticky=tk.NW)
        Label(release_info_frame, text='Disc number', width=15).grid(row=4, column=0)
        no = Entry(release_info_frame, textvariable=self.discno, width=10).grid(row=4, column=1, sticky=tk.NW)

        Label(release_info_frame, text='File name', width=15).grid(row=5, column=0)
        self.file_frame = Frame(release_info_frame)
        Entry(self.file_frame, textvariable=self.filename, width=70).pack(anchor=tk.NW, side=tk.LEFT, padx=10, fill=tk.BOTH)
        FileButton(self.file_frame, False, self.filename, width=10).pack(anchor=tk.NW, side=tk.LEFT, padx=10)

        self.file_frame.grid(row=5, column=1, sticky=tk.NW)
        release_info_frame.pack(anchor=tk.NW, side=tk.TOP, pady=7)
        # no.state(statespec='disabled')

        self.tracks_info_frame = Notebook(self)
        tracks_field = Frame()
        self.tracks_table = TrackFrame()
        self.cue_frame = CueFrame()

        self.tracks_info_frame.add(tracks_field, text='Track list')
        self.tracks_info_frame.add(self.tracks_table, text='Track info')
        self.tracks_info_frame.add(self.cue_frame, text='Cue sheet')

        upper_tracks_frame = Frame(tracks_field, relief=tk.SUNKEN, height=30)
        lower_tracks_frame = Frame(tracks_field, relief=tk.SUNKEN)

        Label(upper_tracks_frame, text='Pattern', width=20).pack(side=tk.LEFT)
        # Entry(upper_tracks_frame, textvariable=self.track_info_pattern, width=50)
        pattern_box = Combobox(upper_tracks_frame,
                               textvariable=self.track_info_pattern,
                               state='active', width=50)  # readonly
        pattern_box['values'] = self.__patterns__
        pattern_box.current(0)
        pattern_box.pack(side=tk.RIGHT, expand=YES)

        upper_tracks_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.NO)

        bar = Scrollbar(lower_tracks_frame)
        self.track_list_box = tk.Text(lower_tracks_frame, relief=tk.SUNKEN)  #, variable=self.track_list)
        lower_tracks_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        bar.config(command=self.track_list_box.yview)
        self.track_list_box.config(yscrollcommand=bar.set)
        self.track_list_box.bind("<Control-Key-a>", self.select_all)
        self.track_list_box.bind("<Control-Key-A>", self.select_all)

        bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.track_list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.tracks_info_frame.pack(anchor=tk.NW, side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=3, pady=5)

        self.next_btn = Button(self, text="Далее", command=self.form_track_table)

        self.tracks_info_frame.bind("<<NotebookTabChanged>>",
               lambda event: self.on_tab_switch(event.widget.index("current")))
        """
        self.tracks_info_frame.bind("<<NotebookTabChanged>>",
               lambda event: event.widget.winfo_children()[event.widget.index("current")].update())
        """

        save_btn = FileButton(self, is_save_btn=True)  # command=self.save_data)
        save_btn.bind("<Button-1>", lambda: self.save_data)
        save_btn.pack(anchor=tk.SE, side=tk.BOTTOM)
        self.next_btn.pack(anchor=tk.SE, side=tk.BOTTOM)

        self.change_release_type()

    def form_track_table(self):
        """
        print("Исполнитель {0}\nАльбом {1}\nДата {2}\nКомментарий {3}\nНомер диска {4}"
              .format(self.artist.get(), self.album.get(), self.date.get(), self.comment.get(), self.discno.get()))
        """
        track_list = self.track_list_box.get('1.0', tk.END+'-1c')
        result = self.parse_tracks(self.track_info_pattern.get(), track_list)
        self.tracks_table.init_fields(result)
        self.tracks_info_frame.select(1)

    def form_cue_sheet(self):
        enumerated_songs = self.tracks_table.get_data()
        release = self.release_type.get()
        file = ""
        if release == "single":
            file = self.filename.get()

        play = Playlist(file,
                        title=self.album.get(),
                        performer=self.artist.get(),
                        date=self.date.get(),
                        songs=[song for s_id, song in enumerated_songs],
                        comment=self.comment.get())
        self.cue_frame.set_cue_sheet(play)
        self.tracks_info_frame.select(2)

    def select_all(self, args):
        self.track_list_box.tag_add(tk.SEL, "1.0", tk.END)
        self.track_list_box.mark_set(tk.INSERT, "1.0")
        self.track_list_box.see(tk.INSERT)
        return 'break'

    def parse_tracks(self, pattern: str, track_list: str) -> List[Tuple[str, Song]]:
        tracks = track_list.split('\n')
        pattern_info = parse_pattern(pattern)
        artist = self.artist.get()
        songs = []

        for track in tracks:  # track - name
            track_info = parse_track(pattern_info, track)
            if track_info == dict():
                continue
            if track_info.get("artist", None) is None:
                track_info["artist"] = artist
            track_number = track_info.get("track", 0)
            track_info.pop("track")
            songs.append((track_number, Song(**track_info)))
        return songs

    def on_tab_switch(self, tab_index: int):
        method = None
        if tab_index == 0:
            method = self.form_track_table
        elif tab_index == 1:
            method = self.form_cue_sheet
        self.next_btn.config(command=method)

        print('click ', tab_index)

    def save_data(self):
        print("Save the world!")

if __name__ == '__main__':
    root = tk.Tk()
    root.style = Style()
    root.style.theme_use("clam")
    root.title("TkSheet helper")

    Form(root).pack(side=tk.TOP, fill=tk.BOTH, expand=YES)
    root.mainloop()
