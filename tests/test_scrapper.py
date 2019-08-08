import pytest

from bs4 import BeautifulSoup
# import difflib

from scrapperlib import syosetu, kakuyomu


@pytest.fixture()
def syosetu_scrapper():
    # SetUp
    # swap get_soup method as to not connect to the internet but use the local file
    def predefined_soup(*args, **kwargs):
        with open("files/syosetu_overview.html", 'r', encoding='utf8') as f:
            return BeautifulSoup(f.read(), features="html.parser")

    scrapper = syosetu.SyosetuScrapper(code='n5715cp')
    scrapper.get_soup = predefined_soup

    # Yield
    yield scrapper

    # TearDown
    del scrapper


@pytest.fixture()
def kakuyomu_scrapper():

    # SetUp
    # swap get_soup method as to not connect to the internet but use the local file
    def predefined_soup(*args, **kwargs):
        with open("files/kakuyomu_overview.html", 'r', encoding='utf8') as f:
            return BeautifulSoup(f.read(), features="html.parser")
    scrapper = kakuyomu.KakuyomuScrapper(code='1177354054882739112')
    scrapper.get_soup = predefined_soup

    # Yield
    yield scrapper

    # TearDown
    del scrapper


class TestSyosetu:
    def test_syosetu_overview_has_title(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()

        assert 'title' in overview, "title missing from overview"

    def test_syosetu_overview_has_chapters(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()

        assert 'chapters' in overview, "chapters list missing from overview"

    def test_syosetu_overview_title_correct(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()

        assert overview['title'] == "そして少女は悪女の体を手に入れる", \
            "title is wrong"

    def test_syosetu_overview_chapters_is_list(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()

        assert isinstance(overview['chapters'], (list, tuple)), \
            "chapters is not a list"

    def test_syosetu_overview_chapter_found(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()

        assert len(overview['chapters']) == 79, "not all chapters found"

    def test_syosetu_overview_chapter_tuple(self, syosetu_scrapper):
        overview = syosetu_scrapper.get_novel_overview()
        ch_t = overview['chapters'][0]

        assert ch_t == ("プロローグ",
                        "https://ncode.syosetu.com/n5715cp/1/"), \
            "chapter tuple not correct"


class TestKakuyomu:

    def test_kakuyomu_overview_has_title(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()

        assert 'title' in overview, "title missing from overview"

    def test_kakuyomu_overview_has_chapters(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()

        assert 'chapters' in overview, "chapters list missing from overview"

    def test_kakuyomu_overview_title_correct(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()

        assert overview['title'] == "ひげを剃る。そして女子高生を拾う。", \
            "title is wrong"

    def test_kakuyomu_overview_chapters_is_list(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()

        assert isinstance(overview['chapters'], (list, tuple)), \
            "chapters is not a list"

    def test_kakuyomu_overview_chapter_found(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()

        assert len(overview['chapters']) == 39, "not all chapters found"

    def test_kakuyomu_overview_chapter_tuple(self, kakuyomu_scrapper):
        overview = kakuyomu_scrapper.get_novel_overview()
        ch_t = overview['chapters'][0]

        assert ch_t == ("プロローグ　電柱の下の女子高生",
                        "https://kakuyomu.jp/works/1177354054882739112/episodes/1177354054882739226"), \
            "chapter tuple not correct"
