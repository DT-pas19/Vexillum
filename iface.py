from tkinter.messagebox import *
from info_widgets import *
from playlist import *


# TODO меню, через которое сделать сохранение в cue файл
# TODO изменение cue файлов
class Form(Frame):

    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()

        self.release_type = tk.StringVar()
        self.artist = tk.StringVar()
        self.album = tk.StringVar()
        self.date = tk.IntVar(value=0)
        self.comment = tk.StringVar()
        self.discno = tk.IntVar(value=1)

        self.filename = tk.StringVar()

        self.i_tabs = None
        self.tracks_field = None
        self.tracks_table = None
        self.cue_frame = None
        self.file_frame = None

        self.next_btn = None

        self.place_widgets()

    def change_release_type(self):
        release = self.release_type.get()
        track_frame_tab = self.i_tabs.tab('1')

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

        self.i_tabs = Notebook(self)
        self.tracks_field = TrackTextFieldFrame()
        self.tracks_table = TrackFrame()
        self.cue_frame = CueFrame()

        self.i_tabs.add(self.tracks_field, text='Track list')
        self.i_tabs.add(self.tracks_table, text='Track info')
        self.i_tabs.add(self.cue_frame, text='Cue sheet')
        self.i_tabs.pack(anchor=tk.NW, side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=3, pady=5)

        self.next_btn = Button(self, text="Далее", command=self.form_track_table)

        self.i_tabs.bind("<<NotebookTabChanged>>",
                         lambda event: self.on_tab_switch(event.widget.index("current")))
        """
        self.tracks_info_frame.bind("<<NotebookTabChanged>>",
               lambda event: event.widget.winfo_children()[event.widget.index("current")].update())
        """

        save_btn = FileButton(self, is_save_btn=True)
        save_btn.bind("<Button-1>", lambda: self.save_data)
        save_btn.pack(anchor=tk.SE, side=tk.BOTTOM)
        self.next_btn.pack(anchor=tk.SE, side=tk.BOTTOM)

        self.change_release_type()

    def form_track_table(self):
        """
        print("Исполнитель {0}\nАльбом {1}\nДата {2}\nКомментарий {3}\nНомер диска {4}"
              .format(self.artist.get(), self.album.get(), self.date.get(), self.comment.get(), self.discno.get()))
        """
        result = self.tracks_field.get_data(self.filename.get(), self.artist.get())
        self.tracks_table.init_fields(result)
        self.i_tabs.select(1)

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
                        comment=self.comment.get(),
                        discnumber=self.discno.get())
        self.cue_frame.set_cue_sheet(play)
        self.i_tabs.select(2)

    @staticmethod
    def select_all(text_field: tk.Text):
        text_field.tag_add(tk.SEL, "1.0", tk.END)
        text_field.mark_set(tk.INSERT, "1.0")
        text_field.see(tk.INSERT)
        return 'break'

    def on_tab_switch(self, tab_index: int):
        method = None
        if tab_index == 0:
            method = self.form_track_table
        elif tab_index == 1:
            method = self.form_cue_sheet
        self.next_btn.config(command=method)

        print('click ', tab_index)


if __name__ == '__main__':
    root = tk.Tk()
    root.style = Style()
    root.style.theme_use("clam")
    root.title("TkSheet helper")

    Form(root).pack(side=tk.TOP, fill=tk.BOTH, expand=YES)
    root.mainloop()
