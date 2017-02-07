from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import *
import tkinter as tk
from os.path import expanduser


class Form(Frame):
    def __init__(self, parent=None, **options):
        Frame.__init__(self, parent, **options)
        self.pack()

        self.release_type = tk.StringVar()
        self.artist = tk.StringVar()
        self.album = tk.StringVar()
        self.date = tk.StringVar()
        self.comment = tk.StringVar()
        self.discno = tk.IntVar(value=1)
        # self.track_list = tk.StringVar()

        self.place_widgets()

    def change_release_type(self):
        release = self.release_type.get()
        if release == "single":
            pass
        if release == "multi":
            pass

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
        Label(release_info_frame, text='Artist', width=20).grid(row=0, column=0)
        Entry(release_info_frame, textvariable=self.artist).grid(row=0, column=1)
        Label(release_info_frame, text='Album', width=20).grid(row=1, column=0)
        Entry(release_info_frame, textvariable=self.album).grid(row=1, column=1)
        Label(release_info_frame, text='Date', width=20).grid(row=2, column=0)
        Entry(release_info_frame, textvariable=self.date).grid(row=2, column=1)
        Label(release_info_frame, text='Comment', width=20).grid(row=3, column=0)
        Entry(release_info_frame, textvariable=self.comment).grid(row=3, column=1)
        Label(release_info_frame, text='Disc number', width=20).grid(row=4, column=0)
        no = Entry(release_info_frame, textvariable=self.discno).grid(row=4, column=1)
        release_info_frame.pack(anchor=tk.NW, side=tk.TOP, pady=7)
        # no.state(statespec='disabled')

        tracks_info_frame = Notebook(self)
        tracks_field = Frame()
        tracks_info_frame.add(tracks_field, text='page1')
        bar = Scrollbar(tracks_field)
        text = tk.Text(tracks_field, relief=tk.SUNKEN)  #, variable=self.track_list)
        bar.config(command=text.yview)
        text.config(yscrollcommand=bar.set)

        bar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        tracks_info_frame.pack(anchor=tk.NW, side=tk.TOP, fill=tk.BOTH, expand=tk.YES, padx=3, pady=5)
        self.track_list_box = text

        Button(self, text="Проверить", command=self.check).pack(anchor=tk.SE, side=tk.BOTTOM)

    def check(self):
        print("Исполнитель {0}\nАльбом {1}\nДата {2}\nКомментарий {3}\nНомер диска {4}"
              .format(self.artist.get(), self.album.get(), self.date.get(), self.comment.get(), self.discno.get()))
        track_list = self.track_list_box.get('1.0', tk.END+'-1c')
        tracks = track_list.split('\n')
        for track in tracks:  # track - name
            parts = track.split(' - ')
            print("{0}. {1}".format(parts[0], parts[1]))


if __name__ == '__main__':
    root = tk.Tk()
    root.style = Style()
    root.style.theme_use("clam")
    root.title("TkSheet helper")

    Form(root).pack(side=tk.TOP, fill=tk.BOTH, expand=YES)
    root.mainloop()
