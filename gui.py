import tkinter as tk
from tkinter import ttk
import threading

import syosetu
import kakuyomu

# Constants
SYOSETU = "syosetu.com"
KAKUYOMU = "kakuyomu.jp"

main_geometry = "300x350"
title = "Web Novel Scrapper"
header = "Choose which novel to scrap!"


class MainWindow:

    def __init__(self):
        # VARIABLES
        self.select_window = None
        self._current_selection = ()
        self.overview = None
        self.book = None

        # WINDOW / ROOT DEFINITION
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(width=False, height=False)
        self.root.geometry(main_geometry)

        # NOVEL CODE ENTRY
        self.novel_lbl = tk.Label(self.root, text="Enter Novel Code:")
        self.novel_lbl.grid(column=0, row=0, columnspan=4, sticky=tk.W,
                            padx=(20, 0), pady=(10, 0))

        self.novel_code = tk.StringVar()
        self.novel = tk.Entry(self.root, width=38,
                              textvariable=self.novel_code)
        self.novel.grid(column=0, row=1, columnspan=4, sticky=tk.W,
                        padx=(20, 0), pady=(0, 5))
        self.novel.focus()

        # WEBSITE SELECTION
        self.website_lbl = tk.Label(self.root, text="Website:")
        self.website_lbl.grid(column=0, row=2, columnspan=4, sticky=tk.W,
                              padx=(20, 0))

        self.website = tk.StringVar()
        self.website_select = \
            ttk.Combobox(self.root, width=13, state="readonly",
                         textvariable=self.website, values=(SYOSETU, KAKUYOMU))
        self.website_select.grid(column=0, row=3, sticky=tk.W, columnspan=4,
                                 padx=(20, 0), pady=(0, 10))
        self.website_select.current(1)
        self.website_select.configure(state="disabled")

        self.infer = tk.BooleanVar()
        self.infer.set(True)

        self.chk = tk.Checkbutton(self.root, text="Infer automatically",
                                  var=self.infer, command=self.infer_changed)
        self.chk.grid(column=1, row=3, sticky=tk.W, columnspan=3,
                      padx=(0, 15), pady=(0, 10))

        # GET CHAPTERS BUTTON
        self.found_chapters_txt = tk.StringVar()

        self.chapters_btn = tk.Button(self.root, text="Get Chapters",
                                      command=self.clicked_get_chapters)
        self.chapters_btn.grid(column=0, row=4, sticky=tk.W,
                               padx=(20, 0), pady=(0, 5))

        self.found_chapters_lbl = \
            tk.Label(self.root, textvariable=self.found_chapters_txt)
        self.found_chapters_lbl.grid(column=1, row=4, sticky=tk.W, padx=(5, 0))

        # ALL CHAPTERS RADIO
        self.chapters_opt = tk.IntVar()

        self.all_chapters_rad = \
            tk.Radiobutton(self.root, text="All Chapters",
                           variable=self.chapters_opt, value=0)
        self.all_chapters_rad.grid(column=0, row=5, sticky=tk.W, padx=(20, 0))

        # CHAPTERS FROM RANGE RADIO
        self.range_chapters_rad = \
            tk.Radiobutton(self.root, text="Range:",
                           variable=self.chapters_opt, value=1)
        self.range_chapters_rad.grid(column=0, row=6, sticky=tk.W,
                                     padx=(20, 0))

        # validation command that only allows digits entered
        vcmd = (self.root.register(
                lambda x: not x or x.isdigit() or x == "\b"),
                '%P')
        self.range_frame = tk.Frame(self.root)
        self.range_frame.grid(column=1, row=6, sticky=tk.W)
        self.ch_from = tk.StringVar()
        self.ch_to = tk.StringVar()
        self.ch_from_entry = tk.Entry(self.range_frame, width=5,
                                      textvariable=self.ch_from,
                                      validate='key', validatecommand=vcmd)
        self.to_label = tk.Label(self.range_frame, text="to")
        self.ch_to_entry = tk.Entry(self.range_frame, width=5,
                                    textvariable=self.ch_to,
                                    validate='key', validatecommand=vcmd)
        self.ch_from_entry.grid(column=0, row=0, sticky=tk.W)
        self.to_label.grid(column=1, row=0, sticky=tk.W)
        self.ch_to_entry.grid(column=2, row=0, sticky=tk.W)
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
            tk.Radiobutton(self.root, text="Select Chapters:",
                           variable=self.chapters_opt, value=2)
        self.select_chapters_rad.grid(column=0, row=7, sticky=tk.W,
                                      padx=(20, 0))

        self.selected_txt = tk.StringVar()
        self.selected_txt.set("Selected: #0")
        self.select_chapters_btn = \
            tk.Button(self.root, textvariable=self.selected_txt,
                      command=self.select_chapters)
        self.select_chapters_btn.grid(column=1, row=7, sticky=tk.W)
        # Select Radio when clicking button
        self.select_chapters_btn.bind("<Button-1>",
                                      lambda e: self.chapters_opt.set(2))

        # DOWNLOAD BUTTON
        self.download_btn = tk.Button(self.root, text="Download",
                                      command=self.clicked_download)
        self.download_btn.grid(column=1, row=8, sticky=tk.E,
                               padx=(0, 20), pady=(20, 0))

    def infer_changed(self):
        if self.infer.get():
            self.website_select.configure(state="disabled")
        else:
            self.website_select.configure(state="readonly")

    def clicked_get_chapters(self):
        code = self.novel_code.get()
        if len(code) == 0:
            return

        if self.infer.get():
            if code[0] == 'n':
                self.website.set(SYOSETU)
            else:
                self.website.set(KAKUYOMU)

        if self.website.get() == SYOSETU:
            self.book = syosetu.SyosetuScrapper(code=code)
        elif self.website.get() == KAKUYOMU:
            self.book = kakuyomu.KakuyomuScrapper(code=code)

        self.found_chapters_txt.set("Connecting to server")

        def get_overview():
            self.chapters_btn.config(state="disabled")

            try:
                self.overview = self.book.get_novel_overview(self.book.get_work_url())
                cnt = len(self.overview['chapters'])
                self.found_chapters_txt.set(f"Found {cnt} chapters")
                self.current_selection = ()
                self.ch_from.set("1")
                self.ch_to.set(str(cnt))
            except AssertionError:
                self.found_chapters_txt.set("Could not find book")
                self.ch_from.set("0")
                self.ch_to.set("0")

            self.chapters_btn.config(state="normal")

        threading.Thread(target=get_overview).start()

    def clicked_download(self):
        self.download_btn.config(state='disabled')

        def full_download():
            self.book.scrap(self.overview, output_folder="")
            self.download_btn.config(state='normal')

        def range_download():
            dl_overview = self.overview.copy()
            start = int(self.ch_from.get())
            end = int(self.ch_to.get())
            dl_overview['chapters'] = dl_overview['chapters'][start-1:end]
            self.book.scrap(dl_overview, output_folder="")
            self.download_btn.config(state='normal')

        def selected_download():
            dl_overview = self.overview.copy()
            dl_overview['chapters'] = \
                [x for i, x in enumerate(dl_overview['chapters'])
                 if i in self.current_selection]
            self.book.scrap(dl_overview, output_folder="")
            self.download_btn.config(state='normal')

        download = {0: full_download, 1: range_download, 2: selected_download}
        threading.Thread(target=download[self.chapters_opt.get()]).start()

    def select_chapters(self):
        if not self.select_window:
            self.select_window = SelectionWindow(self)

    def got_selection(self, selection):
        self.current_selection = selection

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
        self.window.resizable(height=True, width=True)

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
        self.list = tk.Listbox(self.window, selectmode=tk.EXTENDED,
                               yscrollcommand=self.scrollbar)

        if self.main_window.overview:
            size = len(self.main_window.overview['chapters'])
        else:
            size = 0
        for i in range(1, size+1):  # range(len(overview['chapters'])):
            self.list.insert(tk.END, str(i))

        for i in self.main_window.current_selection:
            self.list.select_set(i)

        self.list.pack(side="left", fill=tk.BOTH)
        self.scrollbar.config(command=self.list.yview)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.focus()

    def accept(self):
        """
        Set the current selection of chapters for the main window and close
        """
        selection = self.list.curselection()
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
