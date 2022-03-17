import datetime
import requests
import csv
from pytest import mark
from pytest import fixture
from src.data import DataExtractor
from src.data import URLCollector


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
    return URLCollector(base_url, cities, districts)


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
                "city": str,
                "district": str,
                "region": str,
                "sub-region": str,
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


# TODO redo after URLCollector is improved
class TestUrlCollector:

    @fixture(autouse=True)
    def _init_webscraper(self, url_collector):
        self.url_collector = url_collector

    # TODO this is quite slow...
    def test_get_pages_urls(self):
        self.url_collector.get_pages_urls()

        for _ in range(5):
            try:
                requests.head(self.url_collector.paginated_listings_urls.pop())
            except requests.HTTPError:
                assert False
        assert True

    def test_get_offer_urls_from_pages(self):
        url = self.url_collector.paginated_listings_urls.pop()
        self.url_collector.get_offer_urls_from_page(url)

        for i in range(5):
            try:
                requests.head(self.url_collector.offers_urls[i])
            except requests.HTTPError:
                assert False
        assert True

    def test_get_offer_urls_from_all_pages(self):
        with open("tests/test.csv") as csvfile:
            csv_reader = csv.reader(csvfile)
            for _ in range(5):
                url = csv_reader.__next__()[0]
                requests.head(url)

