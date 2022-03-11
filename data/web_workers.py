from typing import List

from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm
from mpi4py import MPI
from collections import deque
import csv


class JSONUser:
    """Interface for classes that obtain json from otodom website"""
    @staticmethod
    def get_json(url):
        """
        Return json object from given url
        :param url: a string containing url
        :return: json object
        """
        while True:
            try:
                source = requests.get(url).content
                soup = BeautifulSoup(source, "lxml")
                json_string = soup.find("script", id="__NEXT_DATA__")
                data_json = json.loads(json_string.text)

                return data_json["props"]["pageProps"]
            except AttributeError:
                print("Error")
                continue


# TODO make more readable
class URLCollector(JSONUser):
    def __init__(self, base_url, cities, districts):
        self.cities = cities
        self.districts = districts
        self.base_url = base_url
        self.pages_to_visit = deque()
        self.offers_urls = []

    # def get_total_number_of_offers(self):
    #     return self.data_json["pagination"]["totalResults"]

    def get_pages_urls(self):
        for city in self.cities:
            for district in self.districts:
                district_url = f"{self.base_url}/{city}/{district}"
                district_data_json = self.get_json(district_url)["data"]["searchAds"]
                districts_total_number_of_pages = district_data_json["pagination"]["totalPages"]
                for i in tqdm(range(1, districts_total_number_of_pages + 1)):
                    self.pages_to_visit.append(f"{district_url}?page={i}")

    def get_offer_urls_from_page(self, pages_url):
        page_json = self.get_json(pages_url)["data"]["searchAds"]
        for item in page_json["items"]:
            # TODO has to be changed to something less specific/extract url from input
            self.offers_urls.append("https://www.otodom.pl/pl/oferta/" + item["slug"])

    def get_offer_urls_from_all_pages(self):
        comm = MPI.COMM_WORLD
        size = comm.Get_size()
        rank = comm.Get_rank()

        if rank == 0:
            urls = [[] for _ in range(size)]
            self.get_pages_urls()

            i = 0
            while self.pages_to_visit:
                urls[i].append(self.pages_to_visit.pop())
                i = i + 1 if i < size - 1 else 0

        else:
            urls = []

        urls = comm.scatter(urls, root=0)

        for page in tqdm(urls):
            self.get_offer_urls_from_page(page)

        self.offers_urls = comm.gather(self.offers_urls, root=0)
        if rank == 0:
            with open("tests/test.csv", 'w') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=' ')
                for chunk in self.offers_urls:
                    for offer_url in chunk:
                        csv_writer.writerow([offer_url])


class DataExtractor(JSONUser):
    """Used to extract data from a single offer"""

    def __init__(self, url):
        self.data_json = self.get_json(url)["ad"]

    def set_data_json(self, url):
        self.data_json = self.get_json(url)["ad"]

    def get_images(self) -> List[str]:
        """Return a list of strings containing urls of images of an offer"""

        images_urls = []
        images = self.data_json["ad"]["images"]
        for image in images:
            images_urls.append(image["large"])

        return images_urls

    def get_description(self) -> str:
        """Return a string containing description of the offer"""
        soup = BeautifulSoup(self.data_json["description"], "lxml")
        description = soup.get_text(separator=' ')
        return description

    def get_characteristics(self) -> dict:
        """Return a dict containing characteristics of the offer"""
        characteristics_json = self.data_json["characteristics"]
        characteristics = {char["label"].lower(): char["localizedValue"].lower()
                           for char in characteristics_json}
        return characteristics

    def get_date_created(self) -> str:
        """
        Return datetime in %Y-%m-%d %H:%M:%S format of when the offer
        was created
        """
        date_created = self.data_json["dateCreated"]
        return date_created

    def get_date_modified(self) -> str:
        """
        Return datetime string in %Y-%m-%d %H:%M:%S format of when the offer
        was modified
        """
        date_modified = self.data_json["dateModified"]
        return date_modified

    def get_features(self) -> dict:
        """Return a dict containing features of the offer"""
        features_json = self.data_json["featuresByCategory"]
        features = {feature["label"].lower(): feature["values"]
                    for feature in features_json}
        return features

    def get_location(self) -> dict:
        """Return a dict containing location specifications of the offer"""
        location_json = self.data_json["location"]
        location = {
            "address": location_json["address"][0]["value"],
            "coordinates": {
                "latitude": location_json["coordinates"]["latitude"],
                "longitude": location_json["coordinates"]["longitude"],
            },
            "geo_levels": {
                geo_level["type"]: geo_level["label"]
                for geo_level in location_json['geoLevels']
            },
        }

        return location

    # TODO try to figure out what those "statistics" actually are
    # def get_statistics(self):
    #     statistics_json = self.data_json["statistics"]
    #     return json.dumps(statistics_json, indent=4)

    # TODO implement get_all_data function in a sensible way
    # def get_all_data(self):
    #     self.get_images()
    #     self.get_description()
    #     self.get_date_created()
    #     self.get_date_modified()
    #     self.get_features()
    #     self.get_location()


if __name__ == "__main__":
    crawler_cities = ["warszawa"]
    crawler_districts = ["zoliborz", "mokotow", "ochota", "wola"]
    crawler_base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
    webcrawler = URLCollector(crawler_base_url, crawler_cities, crawler_districts)
    webcrawler.get_offer_urls_from_all_pages()
