import bs4
import ssl
import codecs
import threading
import sys
import time
from urllib.request import urlopen, URLError


class Scrapper:
    """
    The superclass of all scrappers that implement the functions to actually rip books for specific websites.
    Subclasses have to implement following functions:
        get_work_url():             Returns the url to the overview page of a book from its site
        get_novel_overview(url):    Returns a dictionary with the title and all chapter links for the book
        extract_chapter(soup):      By passing the soup of a chapter page returns a string in html format of a chapter.
    """
    def __init__(self, threads=1):
        self.threads = threads

    def get_soup(self, url):  # TODO Instead of arg url, create url inside this method
        """
        Connects to the internet and tries to download the html page from the provided url.
        :param url:     Link to the page that will be downloaded
        :return:        Soup object of the downloaded page
        """
        access_try = 1
        while access_try <= 1:
            try:
                context = ssl.SSLContext()
                resp = urlopen(url, context=context)
                break
            except URLError as e:
                print(f"Try {access_try} of 3: Could not access website {url}: " + e.reason, file=sys.stderr)
                access_try += 1
                time.sleep(1)
        else:
            raise AssertionError("There was a problem while accessing the website")

        html = resp.read()
        html = codecs.decode(html)

        soup = bs4.BeautifulSoup(html, features="html.parser")
        return soup

    def get_novel_overview(self, *args, **kwargs):
        raise AssertionError('Method was not implemented by %s' % self.__class__)

    def extract_chapter(self, *args, **kwargs):
        raise AssertionError('Method was not implemented by %s' % self.__class__)

    def get_work_url(self, *args, **kwargs):
        raise AssertionError('Method was not implemented by %s' % self.__class__)

    def write_novel_header(self, output_folder, title, file_nb):
        """
        Creates a new file and writes the header of the html code in it. Returns path to the new file.
        :param output_folder:   The folder in which the new file will be created
        :param title:           The title of the book and therefore of the file
        :param file_nb:         Number of the file
        :return:                The path to the newly created file
        """
        file_path = output_folder + title + " %3d" % file_nb + ".html"
        with open(file_path, 'w', encoding='utf-8') as output:
            string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
            string += title + (" %3d" % file_nb)
            string += '</title>\n<head>\n<body>\n\n'
            output.write(string)
        return file_path

    def create_novels_from_links(self, title, links, output_folder, book_size=-1, verbose=True):
        """
        Called with the links of the chapters which then proceeds to create threads to work on the book.
        :param title:           Name of the novel
        :param links:           A list of all the links to the chapters to be downloaded
        :param output_folder:   Folder in which all files will be created
        :param book_size:       Number of chapters that should go into a single file
        :param verbose:         Boolean that states whether to log current progress
        :return:                None
        """

        chapter_d = dict((i, False) for i in range(len(links)))

        writer = threading.Thread(target=self.thread_writer,
                                  args=(output_folder, title, len(links), chapter_d, book_size, verbose))
        writer.daemon = True
        writer.start()

        link_enumerator = enumerate(links)

        for i in range(self.threads):
            t = threading.Thread(target=self.thread_reader, args=(link_enumerator, chapter_d))
            t.daemon = True
            t.start()

        writer.join()
        if verbose:
            print(output_folder)

    def thread_reader(self, enumerator, chapter_d):
        """
        Function of a reader thread that downloads a chapter.
        :param enumerator:  Enumerator object of the list with the chapter lists
                            (pass the same return value of enumerator() on the list to all threads)
        :param chapter_d:   The dictionary in which the extracted chapter is saved in to guarantee correct order
        :return:            None
        """
        for i, url in enumerator:
            soup = self.get_soup(url)
            chapter_d[i] = self.extract_chapter(soup)

    def thread_writer(self, output_folder, title, total, chapter_d, chapters_per_book=-1, verbose=True):
        """
        Function of the writer thread (only one needed)
        :param output_folder:       Folder in which the files will be created
        :param title:               Title of the novel
        :param total:               Total number of chapters (i.e. length of the chapter links list)
        :param chapter_d:           Dictionary in which all extracted chapters will
                                    be saved in that are ready to be written
        :param chapters_per_book:   Number of chapters that should go into one file
        :param verbose:             Boolean whether or not to log progress on the console
        :return:                    None
        """
        if chapters_per_book == -1:
            chapters_per_book = float('inf')

        file_nb = 0
        current_abs_chapter = 0

        # Loop that will write all chapters
        while current_abs_chapter < total:
            # Prepare a new file
            file_nb += 1  # file_nb is 1 on first loop
            chapters_in_book = 0
            current_file = self.write_novel_header(output_folder, title, file_nb)

            # Write into file until done (chapter count for file reached or no more chapters)
            while chapters_in_book < chapters_per_book and current_abs_chapter < total:
                if not chapter_d[current_abs_chapter]:
                    # Chapter not ready (busy waiting)
                    continue

                # Write chapter into file
                with open(current_file, 'a', encoding='utf-8') as output:
                    if verbose:
                        print('[%d:%d]' % (current_abs_chapter + 1, total))
                    output.write(chapter_d[current_abs_chapter])
                    output.write('\n\n')

                # Save space by deleting finished chapter
                del chapter_d[current_abs_chapter]
                current_abs_chapter += 1
                chapters_in_book += 1

    def scrap(self, overview, output_folder, book_size=-1, first_chapter=0,
              last_chapter=float('inf'), verbose=True):
        """
        Start the process of ripping books from the website.
        :param overview:        Novel overview obtained by
                                Scrapper.get_novel_overview()
        :param output_folder:   Folder in which the files will be created
        :param book_size:       Number of chapters that should go into one file
        :param first_chapter:   The first chapter that should be downloaded
        :param last_chapter:    The last chapter that should be downloaded
        :param verbose:         Boolean whether or not to log current progress
        :return:                None
        """
        # TODO Look at what arguments are needed and stop depending on user input (verbose and quiet option?)

        overview_url = self.get_work_url()

        if last_chapter < float('inf'):
            chapters = overview['chapters'][first_chapter:last_chapter]
        else:
            chapters = overview['chapters'][first_chapter:]

        if verbose:
            print("Starting scrapping:")
            print(overview_url)
            print('Title: \t' + overview['title'])
            print("%d of %d chapters." % (len(chapters), len(overview['chapters'])))

        try:
            self.create_novels_from_links(overview['title'], chapters, output_folder,
                                          book_size=book_size, verbose=verbose)
        except AssertionError as e:
            print("Getting Chapter: " + str(e), file=sys.stderr)
