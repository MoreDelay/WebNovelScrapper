import bs4
import ssl
import codecs
import threading
import os
from urllib.request import urlopen, URLError


class Scrapper:
    """
    The abstract superclass of all scrappers that implement the functions to
    actually rip books for specific websites. Subclasses have to implement
    following functions:
        get_work_url():         Returns the url to the overview page of a
                                book from its site
        get_novel_overview():   Returns a dictionary with the title and all
                                chapter links for the book
        extract_chapter(soup):  By passing the soup of a chapter page returns
                                a string in html format of a chapter.

    Basic usage: Call get_novel_overview() to the title and chapter links.
    Here one can remove some chapter links or the title if needed, and then
    call scrap() with the overview.
    """
    def __init__(self):
        self.running = False
        self.listeners = []
        self.progress = 0
        self.whole = 0
        self.semaphore = threading.Semaphore(0)

    def __init_subclass__(cls, **kwargs):
        # Constraint subclasses to have provide the needed functions
        constraints = ('get_work_url',
                       'get_novel_overview',
                       'extract_chapter')
        for c in constraints:
            assert hasattr(cls, c), f"Please implement the method '{c}' " \
                f"before use."
        return super().__init_subclass__(**kwargs)

    def get_soup(self, url):
        """
        Connects to the internet and tries to download the html page
        from the provided url which is made available as a soup object.
        :param url:     Link to the page that will be downloaded
        :return:        Soup object of the downloaded page
        """
        try:
            context = ssl.SSLContext()
            resp = urlopen(url, context=context)
        except URLError as e:
            raise AssertionError(f"Could not access website {url}: " + e.reason)

        html = resp.read()
        html = codecs.decode(html)

        soup = bs4.BeautifulSoup(html, features="html.parser")
        return soup

    def get_novel_overview(self, *args, **kwargs):
        """
        Implemented by subclasses. Returns an overview dictionary with the
        following content:
            overview = {
                            'title': book_title,
                            'chapters': (chapter_title, link_to_chapter)
                        }
        """
        raise AssertionError(f'Method not implemented by {self.__class__}')

    def extract_chapter(self, *args, **kwargs):
        raise AssertionError(f'Method not implemented by {self.__class__}')

    def get_work_url(self, *args, **kwargs):
        raise AssertionError(f'Method not implemented by {self.__class__}')

    def write_novel_header(self, output_folder, title):
        """
        Creates a new file and writes the header of the html code in it. Returns path to the new file.
        :param output_folder:   The folder in which the new file will be created
        :param title:           The title of the book and therefore of the file
        :param file_nb:         Number of the file
        :return:                The path to the newly created file
        """
        file_path = output_folder + title + ".html"
        with open(file_path, 'w', encoding='utf-8') as output:
            string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
            string += title  # + (" %3d" % file_nb)
            string += '</title>\n<head>\n<body>\n\n'
            output.write(string)
        return file_path

    def create_novels_from_links(self, title, links, output_folder):
        """
        Called with the links of the chapters which then proceeds to create threads to work on the book.
        :param title:           Name of the novel
        :param links:           A list of all the links to the chapters to be downloaded
        :param output_folder:   Folder in which all files will be created
        :param book_size:       Number of chapters that should go into a single file
        :return:                None
        """

        chapter_d = dict((i, False) for i in range(len(links)))

        writer = threading.Thread(target=self.thread_writer,
                                  args=(output_folder, title, len(links), chapter_d))
        writer.daemon = True
        writer.start()

        link_enumerator = enumerate(links)

        t = threading.Thread(target=self.thread_reader, args=(link_enumerator, chapter_d))
        t.daemon = True
        t.start()

        writer.join()

    def thread_reader(self, enumerator, chapter_d):
        """
        Function of a reader thread that downloads a chapter.
        :param enumerator:  Enumerator object of the list with the chapter lists
                            (pass the same return value of enumerator() on the list to all threads)
        :param chapter_d:   The dictionary in which the extracted chapter is saved in to guarantee correct order
        :return:            None
        """
        for i, url in enumerator:
            if self.running:
                soup = self.get_soup(url)
                chapter_d[i] = self.extract_chapter(soup)
                self.semaphore.release()

    def thread_writer(self, output_folder, title, total, chapter_d):
        """
        Function of the writer thread (only one needed)
        :param output_folder:       Folder in which the files will be created
        :param title:               Title of the novel
        :param total:               Total number of chapters
                                    (i.e. length of the chapter links list)
        :param chapter_d:           Dictionary in which all extracted chapters will
                                    be saved in that are ready to be written
        :return:                    None
        """

        assert os.path.isdir(output_folder), f"{output_folder} is not a directory"
        if not output_folder[-1] in ('/', '\\'):
            output_folder += '/'

        cur_chapter_cnt = 0
        current_file = self.write_novel_header(output_folder, title)

        # Loop that will write all chapters
        while cur_chapter_cnt < total and self.running:

            if not chapter_d[cur_chapter_cnt]:
                # Wait for reader to provide new chapter
                # Check whether running is still true after every second
                self.semaphore.acquire(timeout=1)
                continue

            # Write chapter into file
            with open(current_file, 'a', encoding='utf-8') as output:
                output.write(chapter_d[cur_chapter_cnt])
                output.write('\n\n')

            # Save space by deleting finished chapter
            del chapter_d[cur_chapter_cnt]
            cur_chapter_cnt += 1
            self.progress += 1
            self.notify()

    def scrap(self, overview, output_folder=""):
        """
        Start the process of ripping books from the website.
        :param overview:        Novel overview obtained by
                                Scrapper.get_novel_overview()
        :param output_folder:   Folder in which the files will be created
        :param book_size:       Number of chapters that should go into one file
        :return:                None
        """

        chapters = [link[1] for link in overview['chapters']]
        self.running = True
        self.progress = 0
        self.whole = len(overview['chapters'])
        self.notify()

        self.create_novels_from_links(overview['title'], chapters,
                                      output_folder)

    def listen(self, listener):
        assert hasattr(listener, "scrapper_notify"), \
            "Scrapper listener needs a notify function"
        assert callable(listener.scrapper_notify), \
            "Attribute 'scrapper_notify' has to be a function"
        self.listeners.append(listener)

    def unlisten(self, listener):
        self.listeners = [x for x in self.listeners if x is not listener]

    def notify(self):
        for l in self.listeners:
            l.scrapper_notify()
