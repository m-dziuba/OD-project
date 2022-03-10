from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


class JSONUser:  # TODO change the name, this one is bad
    """Interface for classes that obtain json from otodom website"""
    def __init__(self, url):
        self.data_json = self.get_json(url)

    def get_json(self, url):
        """
        Return json object from given url
        :param url: a string containing url
        :return: json object
        """

        source = requests.get(url).content
        soup = BeautifulSoup(source, "lxml")
        json_string = soup.find("script", id="__NEXT_DATA__")
        self.data_json = json.loads(json_string.text)

        return self.data_json["props"]["pageProps"]


# TODO add methods that gather data such as total number of offers per district
# TODO parallelize
class WebCrawler(JSONUser):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url

    def get_links(self):  # TODO modify to accept input urls, districts and such
        number_of_pages = self.data_json["data"]["searchAds"]["pagination"]["totalPages"]
        offers_urls = []
        for i in tqdm(range(1, number_of_pages + 1)):
            url = self.base_url + "?page=" + str(i)
            page_json = self.get_json(url)
            for item in page_json["data"]["searchAds"]["items"]:
                # TODO has to be changed to something less specific/extract url from input
                offers_urls.append("https://www.otodom.pl/pl/oferta/" + item["slug"])

        return offers_urls


class WebScraper(JSONUser):

    def __init__(self, url):
        super().__init__(url)

    def get_images(self):
        """
        Return list of links to images of offers

        :param url: list of offers urls
        :return: list of links to images
        """

        images_urls = []
        images = self.data_json["ad"]["images"]
        for image in images:
            images_urls.append(image["large"])

        return images_urls

    def get_description(self):
        soup = BeautifulSoup(self.data_json["ad"]["description"], "lxml")
        description = soup.get_text(separator=' ')
        return description

    def get_characteristics(self):
        characteristics_json = self.data_json["ad"]["characteristics"]
        characteristics = {char["label"].lower(): char["localizedValue"].lower()
                           for char in characteristics_json}
        return characteristics

    def get_date_created(self):
        date_created = self.data_json["ad"]["dateCreated"]
        return date_created

    def get_date_modified(self):
        date_modified = self.data_json["ad"]["dateModified"]
        return date_modified

    def get_features(self):
        features_json = self.data_json["ad"]["featuresByCategory"]
        features = {feature["label"].lower(): feature["values"]
                    for feature in features_json}
        return features

    def get_location(self):
        location_json = self.data_json["ad"]["location"]
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
    #     statistics_json = self.data_json["ad"]["statistics"]
    #     return json.dumps(statistics_json, indent=4)

    def get_all_data(self):
        self.get_images()
        self.get_description()
        self.get_date_created()
        self.get_date_modified()
        self.get_features()
        self.get_location()


if __name__ == "__main__":
    crawler_source = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/zoliborz"
    scraper_source = "https://www.otodom.pl/pl/oferta/ustawne-dwupokojowe-mieszkanie-na-zoliborzu-ID4fKC3"
    webscraper = WebScraper(scraper_source)
    webscraper.get_location()
    # webcrawler = WebCrawler(crawler_source)
    # crawled_links = webcrawler.get_links()
