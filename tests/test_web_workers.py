import datetime
import requests
from pytest import mark
from pytest import fixture
from data import DataExtractor
from data import UrlCollector


source = 'https://www.otodom.pl/pl/oferta/luksusowy-apartament' \
      '-stary-zoliborz-ID439ZN'

base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
cities = ["warszawa"]
districts = ["zoliborz"]


@fixture(scope="class")
def data_extractor():
    return DataExtractor(source)


@fixture(scope="class")
def url_collector():
    return UrlCollector(base_url, cities, districts)


@mark.data
class TestDataExtractor:

    @fixture(autouse=True)
    def _init_webscraper(self, data_extractor):
        self.data_extractor = data_extractor

    def test_init(self):
        assert isinstance(self.data_extractor.data_json, dict)

    def test_if_tags_in_data_json(self):
        expected_tags = ["images", "description", "dateCreated", "dateModified",
                         "featuresByCategory", "location", "statistics"]

        for tag in expected_tags:
            assert tag in self.data_extractor.data_json

    def test_get_description(self):
        expected_type = str
        obtained_data = self.data_extractor.get_description()
        assert isinstance(obtained_data, expected_type)
        assert obtained_data

    def test_get_characteristics(self):
        expected_type = dict
        obtained_data = self.data_extractor.get_characteristics()
        assert isinstance(obtained_data, expected_type)
        assert obtained_data

    def test_get_date_created(self):
        expected_format = "%Y-%m-%d %H:%M:%S"
        obtained_data = self.data_extractor.get_date_created()

        try:
            datetime.datetime.strptime(obtained_data, expected_format)
        except ValueError:
            assert False
        assert True

    def test_get_date_modified(self):
        expected_format = "%Y-%m-%d %H:%M:%S"
        obtained_data = self.data_extractor.get_date_modified()

        try:
            datetime.datetime.strptime(obtained_data, expected_format)
        except ValueError:
            assert False
        assert True

    def test_get_features(self):
        expected_type = dict
        obtained_data = self.data_extractor.get_features()
        assert isinstance(obtained_data, expected_type)
        assert obtained_data

    def test_get_location(self):
        expected_type = dict
        obtained_data = self.data_extractor.get_location()
        expected_keys_and_types = {
            "address": str,
            "coordinates": {
                "latitude": float,
                "longitude": float,
            },
            "geo_levels": {
                "region": str,
                "sub-region": str,
                "city": str,
            },
        }
        assert isinstance(obtained_data, expected_type)
        for key in expected_keys_and_types.keys():
            inspected_key = expected_keys_and_types[key]
            if isinstance(inspected_key, dict):
                for secondary_key in inspected_key:
                    assert isinstance(obtained_data[key][secondary_key],
                                      inspected_key[secondary_key])
            else:
                assert obtained_data[key] is not None

    # def test_get_statistics(self):
    #     try:
    #         json.loads(self.webscraper.get_statistics())
    #     except ValueError:
    #         assert False
    #     assert True


class TestUrlCollector:

    @fixture(autouse=True)
    def _init_webscraper(self, url_collector):
        self.url_collector = url_collector

    # TODO this is quite slow...
    def test_get_pages_urls(self):
        self.url_collector.get_pages_urls()
        while self.url_collector.pages_to_visit:
            try:
                requests.head(self.url_collector.pages_to_visit.pop())
            except requests.HTTPError:
                assert False
        assert True
