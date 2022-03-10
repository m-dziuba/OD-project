import datetime
import json
from pytest import mark
from pytest import fixture
from webscraping import WebScraper


source = 'https://www.otodom.pl/pl/oferta/luksusowy-apartament' \
      '-stary-zoliborz-ID439ZN'


@fixture(scope="class")
def webscraper():
    return WebScraper(source)


class TestWebScraper:

    @fixture(autouse=True)
    def _init_webscraper(self, webscraper):
        self.webscraper = webscraper

    def test_init(self):
        assert isinstance(self.webscraper.data_json, dict)

    def test_if_tags_in_data_json(self):
        expected_tags = ["images", "description", "dateCreated", "dateModified",
                         "featuresByCategory", "location", "statistics"]

        assert "ad" in self.webscraper.data_json

        for tag in expected_tags:
            assert tag in self.webscraper.data_json["ad"]

    def test_get_description(self):
        expected_type = str
        obtained_data = self.webscraper.get_description()
        assert isinstance(obtained_data, expected_type)

    def test_get_characteristics(self):
        try:
            json.loads(self.webscraper.get_characteristics())
        except ValueError:
            assert False
        assert True

    def test_get_date_created(self):
        expected_format = "%Y-%m-%d %H:%M:%S"
        obtained_data = self.webscraper.get_date_created()

        try:
            datetime.datetime.strptime(obtained_data, expected_format)
        except ValueError:
            assert False
        assert True

    def test_get_date_modified(self):
        expected_format = "%Y-%m-%d %H:%M:%S"
        obtained_data = self.webscraper.get_date_modified()

        try:
            datetime.datetime.strptime(obtained_data, expected_format)
        except ValueError:
            assert False
        assert True

    def test_get_features(self):
        try:
            json.loads(self.webscraper.get_features())
        except ValueError:
            assert False
        assert True

    def test_get_location(self):
        try:
            json.loads(self.webscraper.get_location())
        except ValueError:
            assert False
        assert True

    def test_get_statistics(self):
        try:
            json.loads(self.webscraper.get_statistics())
        except ValueError:
            assert False
        assert True
