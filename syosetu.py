import bs4
import ssl
import codecs
import threading
from urllib.request import urlopen, URLError

import scrapper


class SyosetuScrapper(scrapper.Scrapper):
    urlbase = "https://ncode.syosetu.com"

    def get_novel_overview(self, url):
        res = dict()

        overview_soup = self.get_soup(url)

        title_tag = overview_soup.find(name='p', class_="novel_title")
        res["title"] = title_tag.string

        toc = overview_soup.find(name='div', class_='index_box')
        toc_tags = toc.find_all(name="dd", class_="subtitle")
        episodes = []
        for toc_tag in toc_tags:
            a_tag = toc_tag.find("a")
            episodes.append(a_tag['href'])

        res["episodes"] = episodes
        return res

    def extract_chapter(self, soup):
        res_str = ""
        title_tag = soup.find(name='p', class_='novel_subtitle')
        content_top_tag = soup.find(name='div', id='novel_honbun')

        res_str += "<h2>"
        res_str += title_tag.string
        res_str += "</h2>\n\n"

        for tag in content_top_tag.find_all('p'):
            inter_str = "<p>"
            if tag.get_text() is not "":

                for em in tag.find_all(name='ruby'):
                    if '・' in em.get_text():
                        em.rb.insert(0, '<strong><em>')  # this is evaluated like a string within the tag and
                        em.rb.append('</em></strong>')   # will not create a new tag, thus it will get picked up
                        em.rp.extract()
                        em.rt.extract()
                        em.rp.extract()
                inter_str += tag.get_text()           # by tag.get_text() (and we get our formatting in the output)

            elif tag.contents[0].name == 'br':
                inter_str += "<br/>"

            inter_str += "</p>\n"
            res_str += inter_str

        return res_str
