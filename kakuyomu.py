import bs4
import ssl
import codecs
from urllib.request import urlopen, URLError

URLBASE = "https://kakuyomu.jp"


def get_html(url):
    try:
        context = ssl.SSLContext()
        resp = urlopen(url, context=context)
    except URLError as e:
        print(e.reason)
        return

    html = resp.read()
    html = codecs.decode(html)

    return html


def get_novel_overview(url):
    res = dict()

    html = get_html(url)
    overview_soup = bs4.BeautifulSoup(html, features="html.parser")

    title_tag = overview_soup.find(name='h1', id="workTitle")
    res["title"] = title_tag.string

    toc = overview_soup.find(name='div', class_='widget-toc-main')
    toc_tags = toc.find_all(name="li", class_="widget-toc-episode")
    episodes = []
    for toc_tag in toc_tags:
        a_tag = toc_tag.find("a")
        episodes.append(a_tag['href'])

    res["episodes"] = episodes

    return res


def extract_chapter(html):
    res_str = ""
    soup = bs4.BeautifulSoup(html, features="html.parser")
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


def create_novel_file(name, links, output_path):
    with open(output_path + name + '.html', 'w', encoding='utf-8') as output:
        string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
        string += name
        string += '</title>\n<head>\n<body>\n\n'
        output.write(string)

        for i, link in enumerate(links):
            url = URLBASE + link
            print('[%d:%d]' % (i+1, len(links)), url)
            html = get_html(url)
            output.write(extract_chapter(html))
            output.write('\n\n')

    print(output_path + name + '.html')


def main(output_path):
    number = input("Chapter Number: ")
    if not number.isnumeric():
        print("THIS IS A NUMBER OF A NOVEL")
        return

    work = "/works/" + number
    overview_url = URLBASE + work
    print(overview_url)

    overview = get_novel_overview(overview_url)

    print('TITLE: ' + overview['title'])
    print("%d Chapters." % len(overview['episodes']))

    create_novel_file(overview['title'], overview['episodes'], output_path)

