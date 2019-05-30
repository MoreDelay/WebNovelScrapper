import bs4
import ssl
import codecs
import threading
from urllib.request import urlopen, URLError


class Scrapper:
    urlbase = ""
    thread_cnt = 0
    max_threads = 10  # TODO, this can go into the constructor

    def __init__(self):
        if not self.urlbase:
            raise AssertionError('The value of self.urlbase has to be overwritten by subclasses')
        self.mutex = threading.Lock()  # Mutex for thread_cnt - TODO Rewrite without the need of thread_cnt

    def get_soup(self, url):  # TODO Instead of arg url, create url inside this method
        try:
            context = ssl.SSLContext()
            resp = urlopen(url, context=context)
        except URLError as e:
            print(e.reason)
            return

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
        file_path = output_folder + title + " %3d" % file_nb + ".html"
        with open(file_path, 'w', encoding='utf-8') as output:
            string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
            string += title + (" %3d" % file_nb)
            string += '</title>\n<head>\n<body>\n\n'
            output.write(string)
        return file_path

    def create_novels_from_links(self, title, links, output_folder, book_size=-1, verbose=True):
        # self.write_novel_header(path, title, 1)

        global thread_cnt
        chapter_d = dict((i, False) for i in range(len(links)))

        writer = threading.Thread(target=self.thread_writer,
                                  args=(output_folder, title, len(links), chapter_d, book_size))
        writer.daemon = True
        writer.start()

        for i, link in enumerate(links):
            while thread_cnt >= self.max_threads:
                continue

            self.mutex.acquire()
            thread_cnt += 1
            self.mutex.release()

            if verbose:
                print('[%d:%d]' % (i + 1, len(links)), link)
            t = threading.Thread(target=self.thread_reader, args=(i, link, chapter_d))
            t.daemon = True
            t.start()

        writer.join()
        if verbose:
            print(output_folder)

    def thread_reader(self, i, url, chapter_d):
        soup = self.get_soup(url)
        chapter_d[i] = self.extract_chapter(soup)

        self.mutex.acquire()
        self.thread_cnt -= 1
        self.mutex.release()

    def thread_writer(self, output_folder, title, total, chapter_d, chapters_per_book=-1):
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
                    output.write(chapter_d[current_abs_chapter])
                    output.write('\n\n')

                # Save space by deleting finished chapter
                del chapter_d[current_abs_chapter]
                current_abs_chapter += 1
                chapters_in_book += 1

    def scrap(self, output_folder, book_size=-1, verbose=True):
        # TODO Look at what arguments are needed and stop depending on user input (verbose and quiet option?)

        overview_url = self.get_work_url()
        print(overview_url)

        overview = self.get_novel_overview(overview_url)

        print('Title: \t' + overview['title'])
        print("%d Chapters." % len(overview['chapters']))

        self.create_novels_from_links(overview['title'], overview['chapters'], output_folder,
                                      book_size=book_size, verbose=verbose)
