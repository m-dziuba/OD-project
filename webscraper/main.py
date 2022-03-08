from bs4 import BeautifulSoup
import requests
import json
from tqdm import tqdm


# TODO Rethink the way that urls and other data is obtained.
#  Current system will fail as soon as the website changes


def get_links():
    base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/"
    districts = ["zoliborz"]
    pages = 1
    offer_urls = []

    for i in tqdm(range(1, pages + 1)):
        url = base_url + districts[0] + "?page=" + str(i)
        source = requests.get(url).content
        soup = BeautifulSoup(source, "lxml")
        listings = soup.find("div", role="main").find_all(attrs={"data-cy": "search.listing"})
        # promoted = listings[0].find("ul").find_all("li") # TODO Delete or find a use case
        regular = listings[1].find("ul").find_all("li")
        for offer in regular:
            try:
                link = offer.a["href"]
                offer_urls.append(link)
            except Exception:
                pass

    return offer_urls


def get_images(urls):
    base_url = "https://www.otodom.pl"
    image_urls = []

    for url in tqdm(urls):
        current_url_images = []
        source = requests.get(base_url + url).content
        soup = BeautifulSoup(source, "lxml")

        json_string = soup.find("script", id="__NEXT_DATA__")
        json_obj = json.loads(json_string.text)
        images = json_obj["props"]["pageProps"]["ad"]["images"]
        for image in images:
            current_url_images.append(image["large"])

        image_urls.append(current_url_images)

    return image_urls


def get_descriptions(urls):
    base_url = "https://www.otodom.pl"
    descriptions = []

    for url in tqdm(urls):
        source = requests.get(base_url + url).content
        soup = BeautifulSoup(source, "lxml")

        description_paragraphs = soup.find("section", role="region").find(
            attrs={"data-cy": "adPageAdDescription"}).find_all("p")
        description = "".join([p.text for p in description_paragraphs])
        descriptions.append(description)

    return descriptions


if __name__ == "__main__":
    links_list = get_links()
    # get_images(links_list)
    # get_descriptions(links_list)
