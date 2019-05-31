import scrapper


class SyosetuScrapper(scrapper.Scrapper):
    urlbase = "https://ncode.syosetu.com"

    def __init__(self, code, threads=10):
        """
        Constructor for the Scrapper for syosetu.com.
        Uses threads to have a greater usage of bandwidth and cpu performance, which increases overall speed.
        :param code: The unique code for a book overview page found here: https://ncode.syosetu.com/<CODE>/
        :param threads: Number of threads that request the pages in parallel
        """
        super().__init__(threads)
        self.code = code

    def get_novel_overview(self, url):
        """
        Get title and links to the chapters that will be used in extract_chapter()
        :param url: The link made by get_work_url()
        :return: A dictionary with the fields:
                    'title' - A string of the title of the work.
                    'chapters' - A list of strings that contains all links from which the chapters will be downloaded.
        """
        res = dict()

        overview_soup = self.get_soup(url)

        title_tag = overview_soup.find(name='p', class_="novel_title")
        res["title"] = title_tag.string

        toc = overview_soup.find(name='div', class_='index_box')
        toc_tags = toc.find_all(name="dd", class_="subtitle")
        chapters = []
        for toc_tag in toc_tags:
            a_tag = toc_tag.find("a")
            chapters.append(self.urlbase + a_tag['href'])

        res["chapters"] = chapters
        return res

    def extract_chapter(self, soup):
        """
        Creates a string of a chapter in html format that can be found in the soup object.
        :param soup: Soup of html page for a chapter of a book from syosetu.com
        :return: The chapter in form of a string formatted in html
        """
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

    def get_work_url(self):
        """
        Returns a link to the overview page of a book that holds the links to all its chapters
        :return: The link to the overview page on syosetu.com
        """
        return self.urlbase + '/' + self.code
