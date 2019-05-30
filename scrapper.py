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

    def create_novel_file(self, name, links, folder):
        path = folder + name + '.html'
        with open(path, 'w', encoding='utf-8') as output:
            string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
            string += name
            string += '</title>\n<head>\n<body>\n\n'
            output.write(string)

        global thread_cnt
        chapter_d = dict((i, False) for i in range(len(links)))

        writer = threading.Thread(target=self.thread_writer, args=(path, len(links), chapter_d))
        writer.daemon = True
        writer.start()

        for i, link in enumerate(links):
            while thread_cnt >= self.max_threads:
                continue

            self.mutex.acquire()
            thread_cnt += 1
            self.mutex.release()

            url = self.urlbase + link
            print('[%d:%d]' % (i + 1, len(links)), url)
            t = threading.Thread(target=self.thread_reader, args=(i, url, chapter_d))
            t.daemon = True
            t.start()

        writer.join()
        print(path)

    def thread_reader(self, i, url, chapter_d):
        soup = self.get_soup(url)
        chapter_d[i] = self.extract_chapter(soup)

        self.mutex.acquire()
        self.thread_cnt -= 1
        self.mutex.release()

    def thread_writer(self, path, total, chapter_d):
        to_write = 0
        while to_write < total:
            if not chapter_d[to_write]:
                continue

            with open(path, 'a', encoding='utf-8') as output:
                output.write(chapter_d[to_write])
                output.write('\n\n')

            del chapter_d[to_write]
            to_write += 1

    def scrap(self, output_path, book_size=-1, verbose=True):
        # TODO Look at what arguments are needed and stop depending on user input (verbose and quiet option?)
        code = input("Chapter Code: ")

        work = "/" + code
        overview_url = self.urlbase + work
        print(overview_url)

        overview = self.get_novel_overview(overview_url)

        print('TITLE: ' + overview['title'])
        print("%d Chapters." % len(overview['chapters']))

        self.create_novel_file(overview['title'], overview['chapters'], output_path)
