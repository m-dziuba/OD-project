from bs4 import BeautifulSoup
import requests
import csv


base_url = "https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/warszawa/"
districts = ["zoliborz"]
pages = 12
links = []
csv_file = open('test.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["links"])
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
            csv_writer.writerow([link])
        except Exception:
            pass


print(links)
print(len(links))

csv_file.close()
