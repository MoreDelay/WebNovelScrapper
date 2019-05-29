import bs4
import ssl
import codecs
from urllib.request import urlopen, URLError


# TODO get ready
class Scrapper:

    def get_html(self, url):  # TODO Instead of arg url, create url inside this method
        try:
            context = ssl.SSLContext()
            resp = urlopen(url, context=context)
        except URLError as e:
            print(e.reason)
            return

        html = resp.read()
        html = codecs.decode(html)

        return html

    def get_novel_overview(self, *args, **kwargs):
        raise AssertionError('Method was not implemented by %s' % self.__class__)

    def extract_chapter(self, *args, **kwargs):
        raise AssertionError('Method was not implemented by %s' % self.__class__)
