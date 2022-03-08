from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


# TODO Rethink the way that urls and other data is obtained.
#  Current system will fail as soon as the website changes

base_url = "https://www.otodom.pl/pl/"


def get_json(url):      # TODO read about docstrig convention
    """
    Return json object from given url
    :param url: a string containing url
    :return: json object
    """

    source = requests.get(url).content
    soup = BeautifulSoup(source, "lxml")
    json_string = soup.find("script", id="__NEXT_DATA__")
    json_object = json.loads(json_string.text)

    return json_object["props"]["pageProps"]


def get_links():    # TODO modify to accept input urls, districts and such
    relative_url = "oferty/sprzedaz/mieszkanie/warszawa/"
    districts = ["zoliborz"]
    json_object = get_json(base_url + relative_url + districts[0])
    # pages = json_object["data"]["searchAds"]["pagination"]["totalPages"]
    pages = 1
    offers_urls = []
    for i in tqdm(range(1, pages + 1)):
        url = base_url + relative_url + districts[0] + "?page=" + str(i)
        page_json = get_json(url)
        for item in page_json["data"]["searchAds"]["items"]:
            offers_urls.append(base_url + 'oferta/' + item["slug"])

    return offers_urls


def get_images(urls):
    """
    Return list of links to images of offers

    :param urls: list of offers urls
    :return: list of links to images
    """
    image_urls = []

    for url in tqdm(urls):
        current_url_images = []
        json_object = get_json(url)
        images = json_object["ad"]["images"]
        for image in images:
            current_url_images.append(image["large"])

        image_urls.append(current_url_images)

    return image_urls


def get_descriptions(urls):

    descriptions = []

    for relative_url in tqdm(urls):
        source = requests.get(base_url + relative_url).content
        soup = BeautifulSoup(source, "lxml")

        description_paragraphs = soup.find("section", role="region").find(
            attrs={"data-cy": "adPageAdDescription"}).find_all("p")
        description = "".join([p.text for p in description_paragraphs])
        descriptions.append(description)

    return descriptions


def get_details():
    with open("example.html") as source:
        soup = BeautifulSoup(source, "lxml")

    tags_of_interest = ["characteristics", "dateCreated", "dateModified",
                        "description", "featuresByCategory", "location", "statistics"]
    json_string = soup.find("script", id="__NEXT_DATA__")
    json_obj = json.loads(json_string.text)
    json_features = json_obj["props"]["pageProps"]["ad"]["characteristics"]
    print(print(json.dumps(json_features, indent=4)))


if __name__ == "__main__":
    links_list = get_links()
    get_images(links_list)
    # get_descriptions(links_list)
    # get_details()
