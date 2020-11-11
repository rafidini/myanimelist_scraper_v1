"""
This script contains the code for the web scraper.
"""

# Necessary packages
import requests
from bs4 import BeautifulSoup

# Constants
N_TRY = 20

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
            return False

        # Initiate the BeautifulSoup instance
        self.soup_ = BeautifulSoup(self.response_.text, features="lxml")

        return True

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
        # Some figures
        div_figures = scraper.soup_.find("div", {"class":"po-a di-ib ml12 pl20 pt8"})
        figures = div_figures.find_all("strong")

        # The title
        title = scraper.soup_.find("span", {"itemprop":"name"})

        # Printing
        print(title.get_text(), ":", [fig.get_text() for fig in figures])

def test_scraper_multiplepage_v1():
    """
    This function is used as a testing function for the following objects:
    - WebScraper
    On multiple page.
    """
    search_page = "https://myanimelist.net/manga.php?letter=R"

    scraper = WebScraper(search_page)
    scraper.get()
    scraper.get_soup()

    urls = [link["href"] for link in scraper.soup_.find_all("a", {"class":"hoverinfo_trigger fw-b"})]

    test_scraper_singlepage(urls)

