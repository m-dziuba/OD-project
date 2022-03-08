from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


# TODO Rethink the way that urls and other data is obtained.
#  Current system will fail as soon as the website changes

base_url = "https://www.otodom.pl"


def get_json(url):
    source = requests.get(url).content
    soup = BeautifulSoup(source, "lxml")
    json_string = soup.find("script", id="__NEXT_DATA__")
    json_obj = json.loads(json_string.text)
    return json_obj["props"]["pageProps"]


def get_links():
    relative_url = "/pl/oferty/sprzedaz/mieszkanie/warszawa/"
    districts = ["zoliborz"]
    json_obj = get_json(base_url + relative_url + districts[0])
    pages = json_obj["data"]["searchAds"]["pagination"]["totalPages"]

    offer_urls = []
    for i in tqdm(range(1, pages + 1)):
        url = base_url + relative_url + districts[0] + "?page=" + str(i)
        page_json = get_json(url)
        for item in page_json["data"]["searchAds"]["items"]:
            offer_urls.append(base_url + "/pl/oferta/" + item["slug"])

    return offer_urls


def get_images(urls):
    image_urls = []

    for relative_url in tqdm(urls):
        current_url_images = []
        source = requests.get(base_url + relative_url).content
        soup = BeautifulSoup(source, "lxml")

        json_string = soup.find("script", id="__NEXT_DATA__")
        json_obj = json.loads(json_string.text)
        images = json_obj["props"]["pageProps"]["ad"]["images"]
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
    get_links()
    # get_images(links_list)
    # get_descriptions(links_list)
    # get_details()
