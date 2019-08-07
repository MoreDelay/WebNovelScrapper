import tkinter as tk
from tkinter import ttk
import threading
import os

import syosetu
import kakuyomu

# Constants
SYOSETU = "syosetu.com"
KAKUYOMU = "kakuyomu.jp"

main_geometry = "300x400"
title = "Web Novel Scrapper"
header = "Choose which novel to scrap!"


class MainWindow:

    def __init__(self, path="/"):
        assert isinstance(path, str)

        # VARIABLES
        self.select_window = None
        self._current_selection = ()
        self.overview = None
        self.scrapper = None

        # WINDOW / ROOT DEFINITION
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(width=False, height=False)
        self.root.geometry(main_geometry)

        # NOVEL FRAME
        self.novel_frame = tk.Frame()
        self.novel_frame.grid(column=0, row=0, sticky=tk.W+tk.E,
                              padx=20, pady=(10, 0))
        self.root.grid_columnconfigure(0, weight=1)

        # NOVEL CODE ENTRY
        self.novel_lbl = tk.Label(self.novel_frame, text="Enter Novel Code:")
        self.novel_lbl.grid(column=0, row=0, columnspan=2, sticky=tk.W)

        self.novel_code = tk.StringVar()
        self.novel_entry = tk.Entry(self.novel_frame,
                                    textvariable=self.novel_code)
        self.novel_entry.grid(column=0, row=1, columnspan=2, sticky=tk.W+tk.E,
                              pady=(0, 1))
        self.novel_entry.focus()
        self.novel_frame.grid_columnconfigure(0, weight=1)

        self.destination_lbl = tk.Label(self.novel_frame,
                                        text="Destination Path:")
        self.destination_lbl.grid(column=0, row=2, sticky=tk.W)
        self.destination = tk.StringVar()
        self.destination.set(path)
        self.destination_entry = tk.Entry(self.novel_frame,
                                          textvariable=self.destination)
        self.destination_entry.grid(column=0, row=3, sticky=tk.W+tk.E,
                                    pady=(0, 1))

        # WEBSITE SELECTION
        self.website_lbl = tk.Label(self.novel_frame, text="Website:")
        self.website_lbl.grid(column=0, row=4, sticky=tk.W)

        self.website_frame = tk.Frame(self.novel_frame)
        self.website_frame.grid(column=0, row=5, sticky=tk.W)

        self.website = tk.StringVar()
        self.website_select = \
            ttk.Combobox(self.website_frame, width=14, state="readonly",
                         textvariable=self.website, values=(SYOSETU, KAKUYOMU))
        self.website_select.grid(column=0, row=0, sticky=tk.W)
        self.website_select.current(1)
        self.website_select.configure(state="disabled")

        self.infer = tk.BooleanVar()
        self.infer.set(True)

        self.chk = tk.Checkbutton(self.website_frame, text="Infer automatically",
                                  var=self.infer, command=self.infer_changed)
        self.chk.grid(column=1, row=0, sticky=tk.W)

        # CHAPTERS FRAME
        self.chapters_frame = tk.Frame(self.root)
        self.chapters_frame.grid(column=0, row=1, sticky=tk.W+tk.E,
                                 padx=20, pady=(20, 0))

        # GET CHAPTERS BUTTON
        self.status_txt = tk.StringVar()

        self.chapters_btn = tk.Button(self.chapters_frame, text="Get Chapters",
                                      command=self.on_get_chapters, width=14)
        self.chapters_btn.grid(column=0, row=0, sticky=tk.W, pady=(0, 5))

        self.status_lbl = \
            tk.Label(self.chapters_frame, textvariable=self.status_txt)
        self.status_lbl.grid(column=1, row=0, sticky=tk.W, padx=(5, 0))

        # ALL CHAPTERS RADIO
        self.chapters_opt = tk.IntVar()

        self.all_chapters_rad = \
            tk.Radiobutton(self.chapters_frame, text="All Chapters",
                           variable=self.chapters_opt, value=0)
        self.all_chapters_rad.grid(column=0, row=1, sticky=tk.W)

        # CHAPTERS FROM RANGE RADIO
        self.range_chapters_rad = \
            tk.Radiobutton(self.chapters_frame, text="Range:",
                           variable=self.chapters_opt, value=1)
        self.range_chapters_rad.grid(column=0, row=2, sticky=tk.W)

        # validation command that only allows digits entered
        vcmd = (self.chapters_frame.register(
                lambda x: not x or x.isdigit() or x == "\b"),
                '%P')
        self.range_frame = tk.Frame(self.chapters_frame)
        self.range_frame.grid(column=1, row=2, sticky=tk.W+tk.E)
        self.ch_from = tk.StringVar()
        self.ch_to = tk.StringVar()
        self.ch_from_entry = tk.Entry(self.range_frame, width=5,
                                      textvariable=self.ch_from,
                                      validate='key', validatecommand=vcmd)
        self.to_label = tk.Label(self.range_frame, text="to")
        self.ch_to_entry = tk.Entry(self.range_frame, width=5,
                                    textvariable=self.ch_to,
                                    validate='key', validatecommand=vcmd)
        self.ch_from_entry.grid(column=0, row=0, sticky=tk.W+tk.E)
        self.to_label.grid(column=1, row=0, sticky=tk.W, padx=5)
        self.ch_to_entry.grid(column=2, row=0, sticky=tk.W+tk.E)

        self.chapters_frame.grid_columnconfigure(1, weight=1)
        self.range_frame.grid_columnconfigure(0, weight=1)
        self.range_frame.grid_columnconfigure(2, weight=1)

        # Select Radio when editing
        self.ch_from_entry.bind("<Button-1>",
                                lambda e: self.chapters_opt.set(1))
        self.ch_to_entry.bind("<Button-1>",
                              lambda e: self.chapters_opt.set(1))

        # Initial values
        self.ch_from.set("0")
        self.ch_to.set("0")

        # SELECT CHAPTERS RADIO
        self.select_chapters_rad = \
            tk.Radiobutton(self.chapters_frame, text="Select Chapters:",
                           variable=self.chapters_opt, value=2)
        self.select_chapters_rad.grid(column=0, row=3, sticky=tk.W)

        self.selected_txt = tk.StringVar()
        self.selected_txt.set("Selected: #0")
        self.select_chapters_btn = \
            tk.Button(self.chapters_frame, textvariable=self.selected_txt,
                      command=self.on_select_chapters)
        self.select_chapters_btn.grid(column=1, row=3, sticky=tk.W+tk.E)
        # Select Radio when clicking button
        self.select_chapters_btn.bind("<Button-1>",
                                      lambda e: self.chapters_opt.set(2))

        # DOWNLOAD FRAME
        self.download_frame = tk.Frame(self.root)
        self.download_frame.grid(column=0, row=2, sticky=tk.W+tk.E,
                                 padx=20, pady=(20, 0))
        self.download_frame.grid_columnconfigure(0, weight=1)

        # DOWNLOAD BUTTON
        self.download_btn = tk.Button(self.download_frame, text="Download",
                                      font="Helvetica 12 bold",
                                      command=self.on_download)
        self.download_btn.grid(column=0, row=0, columnspan=2,
                               sticky=tk.W+tk.E)

        # PROGRESS BAR
        self.bar = ttk.Progressbar(self.download_frame, value=0)
        self.bar.grid(column=0, row=1, columnspan=2,
                      pady=(20, 0), sticky=tk.W+tk.E)

        self.progress_text = tk.StringVar()
        self.progress_text.set("0/0")
        self.progress_lbl = tk.Label(self.download_frame,
                                     textvariable=self.progress_text)
        self.progress_lbl.grid(column=0, row=2, sticky=tk.W)

        self.percent_text = tk.StringVar()
        self.percent_text.set("0%")
        self.percent_lbl = tk.Label(self.download_frame,
                                    textvariable=self.percent_text)
        self.percent_lbl.grid(column=1, row=2, sticky=tk.E)

    def infer_changed(self):
        if self.infer.get():
            self.website_select.configure(state="disabled")
        else:
            self.website_select.configure(state="readonly")

    def on_get_chapters(self):
        self.novel_entry.config(background="#FFFFFF")
        self.chapters_btn.config(background="#F0F0F0")
        code = self.novel_code.get()
        if len(code) == 0:
            self.novel_entry.config(background="#FFCCCC")
            return
        if self.infer.get():
            if code[0] == 'n':
                self.website.set(SYOSETU)
            else:
                self.website.set(KAKUYOMU)

        if self.website.get() == SYOSETU:
            self.scrapper = syosetu.SyosetuScrapper(code=code)
        elif self.website.get() == KAKUYOMU:
            self.scrapper = kakuyomu.KakuyomuScrapper(code=code)

        self.status_txt.set("Connecting to server")

        def thread_get_overview():
            self.chapters_btn.config(state="disabled")

            try:
                self.overview = self.scrapper.get_novel_overview()
                cnt = len(self.overview['chapters'])
                self.status_txt.set(f"Found {cnt} chapters")
                self.current_selection = ()
                self.ch_from.set("1")
                self.ch_to.set(str(cnt))
            except AssertionError:
                self.status_txt.set("Could not find book")
                self.ch_from.set("0")
                self.ch_to.set("0")

            self.chapters_btn.config(state="normal")

        t = threading.Thread(target=thread_get_overview)
        t.daemon = True
        t.start()

    def on_download(self):
        self.destination_entry.config(background="#FFFFFF")
        self.chapters_btn.config(background="#F0F0F0")

        if not self.scrapper:
            self.chapters_btn.config(bg="#FFCCCC")
            return

        path = self.destination.get()
        if not os.path.isdir(path):
            self.destination_entry.config(background="#FFCCCC")
            return

        def download_wrapper(fkt):
            def f(*args, **kwargs):
                self.scrapper.listen(self)
                self.download_btn.config(state='disabled')
                self.chapters_btn.config(state='disabled')

                fkt(*args, **kwargs)

                self.download_btn.config(state='normal')
                self.chapters_btn.config(state='normal')
                self.scrapper.unlisten(self)
            return f

        @download_wrapper
        def full_download():
            self.scrapper.scrap(self.overview, output_folder="")

        @download_wrapper
        def range_download():
            dl_overview = self.overview.copy()
            start = int(self.ch_from.get())
            end = int(self.ch_to.get())
            dl_overview['chapters'] = dl_overview['chapters'][start-1:end]
            self.scrapper.scrap(dl_overview, output_folder="")

        @download_wrapper
        def selected_download():
            dl_overview = self.overview.copy()
            dl_overview['chapters'] = \
                [x for i, x in enumerate(dl_overview['chapters'])
                 if i in self.current_selection]
            self.scrapper.scrap(dl_overview, output_folder="")

        download = {0: full_download, 1: range_download, 2: selected_download}
        t = threading.Thread(target=download[self.chapters_opt.get()])
        t.daemon = True
        t.start()

    def on_select_chapters(self):
        if not self.select_window:
            self.select_window = SelectionWindow(self)

    def got_selection(self, selection):
        self.current_selection = selection

    def scrapper_notify(self):
        done = self.scrapper.progress
        whole = self.scrapper.whole
        self.bar.config(value=(done*100)//whole)
        self.percent_text.set(f"{(done * 100) // whole}%")
        self.progress_text.set(f"{done}/{whole}")

    @property
    def current_selection(self):
        return self._current_selection

    @current_selection.setter
    def current_selection(self, t):
        assert isinstance(t, tuple)
        self._current_selection = t
        self.selected_txt.set(f"Selected: #{len(t)}")


class SelectionWindow:

    def __init__(self, main_window):
        self.main_window = main_window

        self.window = tk.Toplevel()
        self.window.title("Chapter Selection")
        self.window.resizable(height=True, width=False)

        # Buttons at the bottom
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(side='bottom')
        self.accept_btn = tk.Button(self.button_frame, text="Accept",
                                    command=self.accept)
        self.accept_btn.pack(side='right')
        self.cancel_btn = tk.Button(self.button_frame, text="Cancel",
                                    command=self.on_closing)
        self.cancel_btn.pack(side='right')

        # chapters list
        self.scrollbar = tk.Scrollbar(self.window)
        self.scrollbar.pack(side="right", fill=tk.Y)
        self.listbox = tk.Listbox(self.window, selectmode=tk.EXTENDED,
                                  yscrollcommand=self.scrollbar.set,
                                  font="helvetica 12")

        if self.main_window.overview:
            chapters = self.main_window.overview['chapters']
            size = len(chapters)
        else:
            size = 0

        for i in range(1, size+1):
            entry = f"{i}:    {chapters[i-1][0]}"
            self.listbox.insert(tk.END, entry)

        for i in self.main_window.current_selection:
            self.listbox.select_set(i)

        self.listbox.config(width=0)
        self.window.geometry("")

        self.listbox.pack(side="left", fill=tk.BOTH)
        self.scrollbar.config(command=self.listbox.yview)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.focus()

    def accept(self):
        """
        Set the current selection of chapters for the main window and close
        """
        selection = self.listbox.curselection()
        self.main_window.got_selection(selection)
        self.on_closing()

    def on_closing(self):
        """
        Close the window and delete reference to this from main window
        """
        self.main_window.select_window = None
        self.window.destroy()


def main():
    main_window = MainWindow()
    main_window.root.mainloop()


main()
