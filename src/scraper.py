"""
This script contains the code for the web scraper.
"""

# Necessary packages
import re
import string
import time

import requests
from bs4 import BeautifulSoup

from model import Artwork

# Constants
N_TRY = 20
LOCATIONS = {
    "name":{"tag":"span", "param":"itemprop", "value":"name"},
    "type":{"tag":"span", "param":"class", "value":"information type"},
    "score":{"tag":"div", "param":"class", "value":re.compile("^score-label score")},
    "rank":{"tag":"span", "param":"class", "value":"numbers ranked"},
    "n_members":{"tag":"span", "param":"class", "value":"numbers members"},
    "popularity":{"tag":"span", "param":"class", "value":"numbers popularity"},
    "synopsis":{"tag":"span", "param":"itemprop", "value":"description"},
    "image":{"tag":"img", "param":"alt", "value":None},
    "genres":{"tag":"span", "param":"itemprop", "value":"genre"},
    "status":{"tag":"div", "param":"class", "value":"dark_text", "check":["Status"]},
    "date":{"tag":"div", "param":"class", "value":"dark_text", "check":["Aired", "Published"]},
    "quantity":{"tag":"div", "param":"class", "value":"dark_text",
    "check":["Chapters", "Episodes"]},
}
STRONGS = ["score", "rank", "popularity", "n_members"]
WAITING_TIME = 15/4

# WebScraper class
class WebScraper:
    """
    This class is a web scraper.
    """

    def __init__(self, url, user_agent=None):
        """
        Constructor of the WebScraper class with the following parameters:
        - url: the web page url
        - user_agent: the user agent
        """
        self.url_ = url
        self.user_agent_ = user_agent
        self.ntry_ = N_TRY
        self.response_ = None
        self.soup_ = None

    def get(self, timeout=10):
        """
        This method will try to connect to the page.
        Return True if the connection has been established otherwise False.
        """
        # The HTTP request
        if self.user_agent_ is None:
            self.response_ = requests.get(self.url_, timeout=timeout)
        else:
            self.response_ = requests.get(self.url_, headers=self.user_agent_, timeout=timeout)

        # Check if the request was successful
        if self.response_.status_code != 200:

            # Check the number of tries
            if self.ntry_ == 0:
                self.ntry_ = N_TRY
                return False
            self.ntry_ -= 1
            return self.get(timeout=timeout)

        return True

    def get_soup(self):
        """
        This method will initiate a BeautifulSoup instance.
        Return True if it worked otherwise False.
        """
        # Check if a request has been made
        if self.response_ is None:
            if not self.get():
                return False

        # Initiate the BeautifulSoup instance
        self.soup_ = BeautifulSoup(self.response_.text, features="lxml")

        return True

    def get_artwork(self):
        """
        This method will extract an artwork from the web page, this method is
        specific to MyAnimeList.net in 12/11/2020.
        Return an Artwork instance.
        """
        # Check if the BeautifulSoup object has been initiated
        if self.soup_ is None:
            if not self.get_soup():
                return None

        # This variable will contain the elements of the artwork
        elements = dict()

        # Loop over the tags
        for key, value in LOCATIONS.items():
            # Image link
            if value["tag"] == "img":
                scraped = self.soup_.find(attrs={value["param"]:elements.get("name")})
                if scraped is not None:
                    elements[key] = scraped.get("data-src")
                continue

            # Genres
            if key == "genres":
                scraped = self.soup_.find_all(attrs={value["param"]:value["value"]})
                elements[key] = [e.get_text() for e in scraped]
                continue

            # Status, Date
            if key in ["status", "date", "quantity"]:
                scraped = self.soup_.find_all(attrs={value["param"]:value["value"]})
                # Loop over the BeautifulSoup elements
                for genre in scraped:
                    # Loop over the potential right tag
                    for substring in value["check"]:
                        # Check if the right tag is found
                        if substring in genre.get_text():
                            elements[key] = genre.find_parent("div").get_text()
                            break

                    if elements.get(key) is not None:
                        break
                continue

            scraped = self.soup_.find(attrs={value["param"]:value["value"]})

            if scraped is not None:
                elements[key] = scraped.get_text()

        return Artwork(name=elements.get("name"),
        art_type=elements.get("type"), score=elements.get("score"),
        rank=elements.get("rank"), popularity=elements.get("popularity"),
        synopsis=elements.get("synopsis"), n_members=elements.get("n_members"),
        image=elements.get("image"), genres=elements.get("genres"),
        status=elements.get("status"), date=elements.get("date"),
        quantity=elements.get("quantity"))

    def is_error_myanimelist(self):
        """
        This method will check if the page from MyAnimeList doesn't
        have an error.
        Return True if error otherwise False.
        """
        # Check the BeautifulSoup instance
        if self.soup_ is None:
            return False

        # Search for the specific error tag
        return self.soup_.find(attrs={"class":"error404"}) is not None

    def get_artwork_urls(self):
        """
        This method will extract the artworks present on the search
        page.
        Return a list of urls.
        """
        # Check the BeautifulSoup instance
        if self.soup_ is None:
            if not self.get_soup():
                return list()

        # Extract the urls
        urls = self.soup_.find_all("a", {"class":re.compile("^hoverinfo_trigger fw-b")})

        # Check if the tags were found
        if urls is None:
            return list()

        return [link["href"] for link in urls]

# MyAnimeListScraper class
class MyAnimeListScraper():
    """
    This class is a scraper specific to MyAnimeList.net, it uses
    the WebScraper class to scrape artworks.
    """

    def __init__(self, urls, ptype=None, pFile=None):
        """
        Constructor of the MyAnimeListScraper class with the following parameters:
        - urls: The base url for the search of animes/manga
        """
        self.urls_ = urls
        self.type_ = ptype
        self.file_ = pFile

    def scrape(self):
        """
        This method will scrape the differents artworks depending on the given
        urls attributes.
        """
        # Variable for the progress
        progress = 1

        # The different letters used for the search
        alphabet = ['.'] + [letter for letter in string.ascii_uppercase]

        # The suffix after the url + letter from alphabet
        suffix = "&show="

        # Loop over the urls
        for url in self.urls_:
            # Progress over alphabet
            progress_alpha = 1

            # Printing the progress
            print("-> URL Progress : {}/{}".format(progress, len(self.urls_)))

            # Loop over the alphabet
            for alpha in alphabet:
                # Printing the progress over the alphabet
                print("  -> ALPHA Progress : {}/{}".format(progress_alpha, len(alphabet)))

                # The variable for the web scraper for the search pages
                search_scraper = None

                # Initiating the increnmenting variable for the no pages
                no_page = 0

                # Loop over the pages
                while True:

                    # The complete url
                    search_page_url = "{}{}{}{}".format(url, alpha, suffix, no_page)

                    # Initiating the web scraper
                    search_scraper = WebScraper(search_page_url)
                    search_scraper.get()
                    search_scraper.get_soup()

                    # The break point
                    if search_scraper.is_error_myanimelist():
                        break

                    # Get the artwork urls
                    artworks_urls = search_scraper.get_artwork_urls()

                    # Progress over the artworks
                    progress_artworks = 1

                    # Scraping the artworks
                    for artwork_url in artworks_urls:
                        print("    -> ARTWORK Progress : {}/{}".format(progress_artworks, len(artworks_urls)))
                        artwork_scraper = WebScraper(artwork_url)
                        time.sleep(WAITING_TIME)
                        progress_artworks += 1

                        # Try to scrape
                        if not artwork_scraper.get():
                            return False

                        # Try to initiate the BeautifulSoup instance
                        if artwork_scraper.get_soup():
                            artwork = artwork_scraper.get_artwork()
                            self.file_.write(artwork.to_csv())
                            self.file_.write("\n")

                    # Incrementation
                    no_page += 50

                    # Wait a second
                    time.sleep(WAITING_TIME)

                # Incrementation of the progress alpha
                progress_alpha +=1
            
            # Incrementation of the progress
            progress +=1
        return True

# Personal est functions
def test_scraper_singlepage(urls):
    """
    This function is used as a testing function for the following objects:
    - WebScraper
    On a single page.
    """

    for url in urls:
        scraper = WebScraper(url)
        scraper.get()
        scraper.get_soup()
        print(scraper.get_artwork())

def test_scraper_multiplepage_v1():
    """
    This function is used as a testing function for the following objects:
    - WebScraper
    On multiple page.
    """
    search_page = "https://myanimelist.net/anime.php?letter=N&show=150"

    scraper = WebScraper(search_page)
    scraper.get()
    scraper.get_soup()

    urls = [
        link["href"] for link in scraper.soup_.find_all(
            "a", {"class":re.compile("^hoverinfo_trigger fw-b")})
    ]

    test_scraper_singlepage(urls)
