from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


# TODO make a get method for each of tags. Maybe covert to class? Change get_details


base_url = "https://www.otodom.pl/pl/"

tags_of_interest = ["characteristics", "dateCreated", "dateModified",
                    "description", "featuresByCategory", "location", "statistics"]


class JSONUser:     # TODO change the name, this one is bad

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


class WebCrawler(JSONUser):
    def __init__(self, url):
        super().__init__(url)

    def get_links(self):    # TODO modify to accept input urls, districts and such
        relative_url = "oferty/sprzedaz/mieszkanie/warszawa/"
        districts = ["zoliborz"]
        self.data_json = self.get_json(base_url + relative_url + districts[0])
        # pages = json_object["data"]["searchAds"]["pagination"]["totalPages"]
        pages = 1
        offers_urls = []
        for i in tqdm(range(1, pages + 1)):
            url = base_url + relative_url + districts[0] + "?page=" + str(i)
            page_json = self.get_json(url)
            for item in page_json["data"]["searchAds"]["items"]:
                offers_urls.append(base_url + 'oferta/' + item["slug"])

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
        return json.dumps(characteristics_json, indent=4)      # TODO change to dict label: localizedValue

    def get_date_created(self):
        date_created = self.data_json["ad"]["dateCreated"]
        return date_created

    def get_date_modified(self):
        date_modified = self.data_json["ad"]["dateModified"]
        return date_modified

    def get_features(self):
        features_json = self.data_json["ad"]["featuresByCategory"]
        return json.dumps(features_json, indent=4)

    def get_location(self):
        location_json = self.data_json["ad"]["location"]
        return json.dumps(location_json, indent=4)

    def get_statistics(self):
        statistics_json = self.data_json["ad"]["statistics"]
        return json.dumps(statistics_json, indent=4)


if __name__ == "__main__":
    sauce = "https://www.otodom.pl/pl/oferta/ustawne-dwupokojowe-mieszkanie-na-zoliborzu-ID4fKC3"
    webscraper = WebScraper(sauce)
    print(webscraper.get_images())
    print(webscraper.get_description())
    print(webscraper.get_characteristics())
    print(webscraper.get_date_created())
    print(webscraper.get_date_modified())
    print(webscraper.get_features())
    print(webscraper.get_location())
    print(webscraper.get_statistics())
