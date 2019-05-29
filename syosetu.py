import bs4
import ssl
import codecs
import threading
from urllib.request import urlopen, URLError

URLBASE = "https://ncode.syosetu.com"

thread_cnt = 0
max_threads = 10
mutex = threading.Lock()


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


def extract_chapter(html):
    res_str = ""
    soup = bs4.BeautifulSoup(html, features="html.parser")
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


def thread_reader(i, url, chapter_d):
    html = get_html(url)
    chapter_d[i] = extract_chapter(html)

    global thread_cnt
    mutex.acquire()
    thread_cnt -= 1
    mutex.release()


def thread_writer(path, total, chapter_d):
    to_write = 0
    while to_write < total:
        if not chapter_d[to_write]:
            continue

        with open(path, 'a', encoding='utf-8') as output:
            output.write(chapter_d[to_write])
            output.write('\n\n')

        del chapter_d[to_write]
        to_write += 1


def create_novel_file(name, links, folder):
    path = folder + name + '.html'
    with open(path, 'w', encoding='utf-8') as output:
        string = '\n<html>\n<head>\n<meta charset="utf-8">\n<title>'
        string += name
        string += '</title>\n<head>\n<body>\n\n'
        output.write(string)

    global thread_cnt
    chapter_d = dict((i, False) for i in range(len(links)))

    writer = threading.Thread(target=thread_writer, args=(path, len(links), chapter_d))
    writer.daemon = True
    writer.start()

    for i, link in enumerate(links):
        while thread_cnt >= max_threads:
            continue

        mutex.acquire()
        thread_cnt += 1
        mutex.release()

        url = URLBASE + link
        print('[%d:%d]' % (i + 1, len(links)), url)
        t = threading.Thread(target=thread_reader, args=(i, url, chapter_d))
        t.daemon = True
        t.start()

    writer.join()
    print(path)


def main(output_path):
    code = input("Chapter Code: ")

    work = "/" + code
    overview_url = URLBASE + work
    print(overview_url)

    overview = get_novel_overview(overview_url)

    print('TITLE: ' + overview['title'])
    print("%d Chapters." % len(overview['episodes']))

    create_novel_file(overview['title'], overview['episodes'], output_path)

