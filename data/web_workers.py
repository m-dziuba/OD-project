from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


class JSONUser:  # TODO change the name, this one is bad
    """Interface for classes that obtain json from otodom website"""
    @staticmethod
    def get_json(url):
        """
        Return json object from given url
        :param url: a string containing url
        :return: json object
        """

        source = requests.get(url).content
        soup = BeautifulSoup(source, "lxml")
        json_string = soup.find("script", id="__NEXT_DATA__")
        data_json = json.loads(json_string.text)

        return data_json["props"]["pageProps"]


# TODO parallelize
class WebCrawler(JSONUser):
    def __init__(self, base_url, cities, districts):
        self.cities = cities
        self.districts = districts
        self.base_url = base_url
        self.pages_to_visit = []
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
        current_page_json = self.get_json(pages_url)["data"]["searchAds"]
        for item in current_page_json["items"]:
            # TODO has to be changed to something less specific/extract url from input
            self.offers_urls.append("https://www.otodom.pl/pl/oferta/" + item["slug"])

    def get_offer_urls_from_all_pages(self):
        self.get_pages_urls()
        for page in tqdm(self.pages_to_visit):
            self.get_offer_urls_from_page(page)


class WebScraper(JSONUser):

    def __init__(self, url):
        self.data_json = self.get_json(url)["ad"]

    def get_images(self):
        """
        Return list of urls of images of an offer

        :return: list of urls of images
        """

        images_urls = []
        images = self.data_json["ad"]["images"]
        for image in images:
            images_urls.append(image["large"])

        return images_urls

    def get_description(self):
        soup = BeautifulSoup(self.data_json["description"], "lxml")
        description = soup.get_text(separator=' ')
        return description

    def get_characteristics(self):
        characteristics_json = self.data_json["characteristics"]
        characteristics = {char["label"].lower(): char["localizedValue"].lower()
                           for char in characteristics_json}
        return characteristics

    def get_date_created(self):
        date_created = self.data_json["dateCreated"]
        return date_created

    def get_date_modified(self):
        date_modified = self.data_json["dateModified"]
        return date_modified

    def get_features(self):
        features_json = self.data_json["featuresByCategory"]
        features = {feature["label"].lower(): feature["values"]
                    for feature in features_json}
        return features

    def get_location(self):
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
    # scraper_source = "https://www.otodom.pl/pl/oferta/ustawne-dwupokojowe-mieszkanie-na-zoliborzu-ID4fKC3"
    # webscraper = WebScraper(scraper_source)
    # webscraper.get_location()
    crawler_cities = ["warszawa"]
    crawler_districts = ["zoliborz", "mokotow", "ochota", "wola"]
    crawler_base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie"
    webcrawler = WebCrawler(crawler_base_url, crawler_cities, crawler_districts)
    # crawled_links = webcrawler.get_links()
    # print(crawled_links)
    # print(len(crawled_links) == webcrawler.get_total_number_of_offers())
    webcrawler.get_offer_urls_from_all_pages()
