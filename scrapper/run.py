import os

import pandas as pd
from beer_scrapper import BeerScraper
from constants import COOKIES, FOLDER


# run scrapper
def run_scrapper():
    scraper = BeerScraper(cookies=COOKIES, pages=1)
    brewery, beer, comment, style = scraper.start_scraping()
    pd.DataFrame(brewery).to_csv(os.path.join(FOLDER, "brewery.csv"))
    pd.DataFrame(beer).to_csv(os.path.join(FOLDER, "beer.csv"))
    pd.DataFrame(comment).to_csv(os.path.join(FOLDER, "comment.csv"))
    pd.DataFrame(style).to_csv(os.path.join(FOLDER, "style.csv"))
