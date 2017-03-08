"""
Test polygon used for learning tk basics
"""

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.ttk as ttk
from os.path import expanduser


class OpenFileButton(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        self.__btn__ = Button(self, text='Открыть', width=15, command=self.action)
        self.__btn__.bind('<Control-Button-1>', self.save_action)
        self.__btn__.bind('<Control-Enter>', lambda x: self.__btn__.config(text='Сохранить'))
        self.__btn__.bind('<Control-Motion>', lambda x: self.__btn__.config(text='Сохранить-2'))
        self.__btn__.bind('<Leave>', lambda x: self.__btn__.config(text='Открыть'))
        self.__btn__.bind('<KeyRelease>', self.release)
        self.__btn__.pack(side=TOP, expand=YES, fill=BOTH)

    def action(self):
        home = expanduser("~")
        ask = askopenfilename(initialdir=home,
                              title='Выбор звукового файла',
                              filetypes=(("Lossless flac", "*.flac"),
                                         ("MPEG Layer-3", "*.mp3"),
                                         ("Monkey's Audio", "*.ape"),
                                         ("All Files", "*.*"))
                              )
        print('Было передано для открытия \'{0}\''.format(ask))

    def save_action(self, args):
        ask = asksaveasfilename()
        print('Было передано для сохранения \'{0}\''.format(ask))
        print('Аргументы {0}'.format(args))

    def release(self, event):
        print("Отпущена клавиша {0}".format(event.keysym))
        if event.keysym == 'Control_L':
            self.__btn__.config(text='Открыть-2')


def act(arg):
    print("Передано {0}", type(arg))


def act_strange(e: Event):
    app_highlight_font = ('Helvetica', 20, 'bold')
    app_ordinary_font = ('times', 18, 'normal')
    e.widget.config(font=app_highlight_font, bg='black', fg='yellow')
    e.widget.config(width=30, height=3)
    # if e.widget.font == app_highlight_font:
    #        e.widget.config(font=app_ordinary_font)
    # else:


def callback(e: Event):
    if askyesno('Approval is required', 'Do you want to change the font?'):
        app_highlight_font = ('Helvetica', 20, 'bold')
        e.widget.config(font=app_highlight_font, bg='black', fg='yellow')
        showwarning('Result', 'WYSIWYG!')
    else:
        app_ordinary_font = ('times', 14, 'normal')
        e.widget.config(font=app_ordinary_font, bg='white', fg='black')
        showinfo("Result", "The font settings were reset")


def custom_dialog():
    win = Toplevel()
    Label(win, text="Well, hello then!").pack(side=TOP)
    Button(win, text="Alright...", width=10, command=win.destroy).pack(side=TOP)
    win.focus_set()
    win.grab_set()
    win.wait_window()
    print('Диалог отрисовался')

root = Tk()
root.style = ttk.Style()
#('clam', 'alt', 'default', 'classic')
root.style.theme_use("clam")

win = Frame(root)
win.pack()
widget_1 = Label(win)
widget_1.config(text="Hello again")
widget_1.pack(side=TOP, expand=Y)
widget_2 = Button(win)
widget_2.config(text="Another one", width=80)
widget_2.bind('<Button-1>', act)
widget_2.bind('<Control-Button-1>', lambda x: callback(x))
# widget_2.bind('<Control-Button-1>', lambda x: act_strange(x))
widget_2.pack(expand=YES, fill=BOTH, side=RIGHT)
Button(win, text="Press", command=lambda: print("The button is pressed")).pack(side=TOP)
OpenFileButton(win).pack(side=TOP)
Button(text="Popup head lights", width=15, command=custom_dialog).pack(side=TOP)

root.title("Main GUI module")
root.mainloop()
