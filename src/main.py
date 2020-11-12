"""
This script contains the code for the app.
"""

from scraper import MyAnimeListScraper
from model import Artwork
from path import DATA_PATH

# Base urls needed for the scraping
urls = [
    "https://myanimelist.net/anime.php?letter=",
    "https://myanimelist.net/manga.php?letter=",
]

# Open file
f = open(DATA_PATH, "a")

# Initiate the scraper
scraper = MyAnimeListScraper(urls, pFile=f)

# Write the csv header
f.write(Artwork.csv_header())
f.write("\n")

# Begin the scraping
print("Scraping in process...")
scraper.scrape()
print("Finished!")

# Close file
f.close()
