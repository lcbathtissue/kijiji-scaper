import csv

import requests
from bs4 import BeautifulSoup

# ORIGINALLY INTENDED TO FIND RENTAL PROPERTIES / APARTMENTS

kijiji_area = "oshawa-durham-region"
kijiji_section_ID = "c37l1700275"

URLS = [
    "https://4rent.ca/apartments-for-rent/on/oshawa/4497/list",
    "https://www.rentcafe.com/apartments-for-rent/ca/on/oshawa/",
    f"https://www.kijiji.ca/b-apartments-condos/{kijiji_area}/{kijiji_section_ID}",
    "https://www.viewit.ca/vwListings.aspx?bedrooms=0&CID=33&cs=1",
    "https://www.viewit.ca/vwListings.aspx?bedrooms=1&CID=33&cs=1",
    "https://www.viewit.ca/vwListings.aspx?bedrooms=2&CID=33&cs=1",
    "https://rentals.ca/oshawa",
]

listings = []

class listing:
    def __init__(self):
        self.site = None
        self.price = None
        self.URL = None
    def set_site(self, site):
        self.site = site
    def set_price(self, price):
        self.price = price
    def set_URL(self, URL):
        self.URL = URL
    def get_site(self):
        return self.site
    def get_price(self):
        return self.price
    def get_URL(self):
        return self.URL


def scrapeApartments(URL):
    show_errors = False
    r = requests.get(URL)
    data = r.text
    soup = BeautifulSoup(data, features="lxml")
    site = None
    pages = None
    current_page_num = 1
    highest_page_num = None
    if URL.find("kijiji") != -1:
        site = "kijiji"
        pages = []
        page_div = soup.find("div", {"class": "pagination"})
        highest_page_num = 0
        # find the maximum page number
        for anchor_tag in page_div.find_all("a"):
            page_num = str(anchor_tag.encode_contents())[2:-1]
            if len(page_num) == 1 or len(page_num) == 2:
                if int(page_num) > int(highest_page_num):
                    highest_page_num = int(page_num)
        # generate valid URL's for the different pages
        # based on the max found page number and site
        for count in range(1, highest_page_num+1):
            tag = URL[len(URL)-11:]
            if count == 2:
                URL = URL[:-11]
                URL = f"{URL}page-{count}/{tag}"
            elif count > 2:
                URL = URL[:-13]
                URL = f"{URL}{count}/{tag}"
            pages.append(URL)

    for index, URL in enumerate(pages):
        print(f"Scraping {site} page {index+1}/{highest_page_num}..")
        r = requests.get(URL)
        data = r.text
        soup = BeautifulSoup(data, features="lxml")
        for listing_div in soup.find_all("div", {"class": "search-item"}):
            error_in_scrape = None
            price = None
            href = None
            for price_div in listing_div.find_all("div", {"class": "price"}):
                try:
                    if site == "kijiji":
                        price = str(price_div.encode_contents()[187:187+8])[2:-1]
                        price = price.replace(",", "")
                        price = float(price)
                except ValueError:
                    if show_errors:
                        error_in_scrape = True
                        print("something went wrong")
            if error_in_scrape is not True:
                for title_div in listing_div.find_all("div", {"class": "title"}):
                    title = str(title_div.encode_contents())
                    href = title[title.find('href="')+len('href="'):]
                    href = href[:href.find('"')]
                    href = "https://www.kijiji.ca" + href
            if price == "Please C":
                price = "N/A"
            listings.append(listing())
            listings_index = len(listings)-1
            listings[listings_index].set_site(site)
            listings[listings_index].set_price(price)
            listings[listings_index].set_URL(href)
        # with open("raw.html", "w", encoding="utf-8") as displayHTML:
        #     displayHTML.write(raw)
        # displayHTML.close()
    return listings


found_apartments = scrapeApartments("https://www.kijiji.ca/b-apartments-condos/oshawa-durham-region/c37l1700275")

# for i in range(1, len(found_apartments)):
#     key = found_apartments[i].get_price()
#     j = i - 1
#     if key == "N/A":
#         key = -1
#     else:
#         key = float(key)
#     while j >= 0 and key < found_apartments[j].get_price():
#         found_apartments[j + 1].set_price(found_apartments[j].get_price())
#         j -= 1
#     if key != -1:
#         found_apartments[j + 1].set_price(key)
#     else:
#         found_apartments[j + 1].set_price("N/A")



for apt in found_apartments:
    site = apt.get_site()
    price = apt.get_price()
    URL = apt.get_URL()
    if price != "N/A":
        price = "$" + str(price)
    print(f"[{site}] {price}: {URL}")
    with open('output.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow([site, price, f'=HYPERLINK("{URL}")'])
    csvfile.close()
