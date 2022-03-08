from bs4 import BeautifulSoup
import requests
import csv
import json
import pandas as pd


def crawl():
    base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/"
    districts = ["zoliborz"]
    pages = 12
    links = []
    # csv_file = open('test.csv', 'w')
    # csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(["links"])
    for i in range(1, pages + 1):
        print(f"{i}/{pages}")
        url = base_url + districts[0] + "?page=" + str(i)
        source = requests.get(url).content
        soup = BeautifulSoup(source, "lxml")
        listings = soup.find("div", role="main").find_all(attrs={"data-cy": "search.listing"})
        promoted = listings[0].find("ul").find_all("li")
        regular = listings[1].find("ul").find_all("li")
        for offer in regular:
            try:
                link = offer.a["href"]
                links.append(link)
                # csv_writer.writerow([link])
            except Exception:
                pass
    # csv_file.close()
    return links


def scrape():
    with open("example.html") as source:
        soup = BeautifulSoup(source, "lxml")

    json_string = soup.find("script", id="__NEXT_DATA__")
    links = []
    obj = json.loads(json_string.text)
    images = obj["props"]["pageProps"]["ad"]["images"]
    for image in images:
        links.append(image["large"])
    print(links)

if __name__ == "__main__":
    # links_list = crawl()
    scrape()
