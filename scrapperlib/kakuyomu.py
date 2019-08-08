from scrapperlib import scrapper


class KakuyomuScrapper(scrapper.Scrapper):
    urlbase = "https://kakuyomu.jp"

    def __init__(self, code):
        """
        Constructor for the Scrapper for kakuyomu.jp.
        Uses threads to have a greater usage of bandwidth and cpu performance, which increases overall speed.
        :param code: The unique code for a book overview page found here: https://kakuyomu.jp/works/<CODE>
        """
        super().__init__()
        self.code = str(code)

    def get_novel_overview(self):
        """
        Get title and links to the chapters that will be used in extract_chapter()
        :return: A dictionary with the fields:
                    'title' - A string of the title of the work.
                    'chapters' - A list of strings that contains all links from which the chapters will be downloaded.
        """
        res = dict()

        overview_soup = self.get_soup(self.get_work_url())

        title_tag = overview_soup.find(name='h1', id="workTitle")
        res["title"] = title_tag.string

        toc = overview_soup.find(name='div', class_='widget-toc-main')
        toc_tags = toc.find_all(name="li", class_="widget-toc-episode")
        chapters = []
        for toc_tag in toc_tags:
            a_tag = toc_tag.find("a")
            link = self.urlbase + a_tag['href']
            a_tag = a_tag.find("span")
            ch_title = a_tag.get_text()
            chapters.append((ch_title, link))

        res["chapters"] = chapters
        return res

    def extract_chapter(self, soup):
        """
        Creates a string of a chapter in html format that can be found in the soup object.
        :param soup: Soup of html page for a chapter of a book from kakuyomu.jp
        :return: The chapter in form of a string formatted in html
        """
        res_str = ""
        title_tag = soup.find(name='p', class_='widget-episodeTitle')
        content_top_tag = soup.find(name='div', class_='widget-episodeBody')

        res_str += "<h2>"
        res_str += title_tag.string
        res_str += "</h2>\n\n"

        for tag in content_top_tag.find_all('p'):
            inter_str = "<p>"
            if tag.get_text() is not "":

                for em in tag.find_all(name='em', class_='emphasisDots'):
                    em.insert(0, '<strong><em>')  # this is evaluated like a string within the tag and
                    em.append('</em></strong>')   # will not create a new tag, thus it will get picked up
                inter_str += tag.get_text()       # by tag.get_text() (and we get our formatting in the output)

            elif tag.contents[0].name == 'br':
                inter_str += "<br/>"

            inter_str += "</p>\n"
            res_str += inter_str

        return res_str

    def get_work_url(self):
        """
        Returns a link to the overview page of a book that holds the links to all its chapters
        :return: The link to the overview page on kakuyomu.jp
        """
        return self.urlbase + '/works/' + self.code
