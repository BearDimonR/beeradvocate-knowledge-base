import os

import numpy as np
import pandas as pd
from scrapper.beer_scrapper import BeerScraper
from constants import COOKIES, FOLDER

import warnings

warnings.filterwarnings("ignore")


def normalize(parsed_brewery):
    df_breweries = pd.DataFrame(parsed_brewery)
    df_locations = df_breweries[
        ["brewery_city", "brewery_country", "brewery_province"]
    ].drop_duplicates()
    df_locations["location_id"] = df_locations.index
    df_breweries["brewery_location_id"] = df_breweries["brewery_city"].apply(
        lambda name: df_locations.loc[
            df_locations["brewery_city"] == name
        ].index[0]
    )
    df_breweries = df_breweries.drop(
        columns=["brewery_city", "brewery_country", "brewery_province"]
    )

    adjusted_brewery = df_breweries.to_dict(orient="records")
    adjusted_location = df_locations.to_dict(orient="records")

    return (
        adjusted_brewery,
        adjusted_location,
    )


def process(location, brewery, beer, comment, style):
    df_location = pd.DataFrame(location).rename(
        columns={
            "brewery_city": "city",
            "brewery_country": "country",
            "brewery_province": "province",
            "location_id": "id",
        }
    )

    df_brewery = pd.DataFrame(brewery).rename(
        columns={
            "brewery_name": "name",
            "brewery_number": "id",
            "brewery_beer_number": "count_beers",
            "brewery_beer_ratings": "count_ratings",
            "brewery_beer_score": "avg_score",
            "brewery_location_id": "location_id",
        }
    )

    df_beer = pd.DataFrame(beer).rename(
        columns={
            "beer_name": "name",
            "beer_number": "id",
            "brewery_number": "brewery_id",
            "brewery_name": "brewery_name",
            "beer_style": "style_id",
            "beer_abv": "abv",
            "beer_avg": "avg",
            "beer_score": "score",
            "beer_pDev": "pdev",
            "beer_reviews": "count_reviews",
            "beer_ratings": "count_ratings",
            "beer_status": "status",
            "beer_rated": "date_rated",
            "beer_added": "date_added",
            "beer_added_user": "creator",
            "beer_wants": "count_wants",
            "beer_gots": "count_gots",
            "beer_description": "description",
        }
    )
    df_beer["abv"] = (
        df_beer["abv"]
        .replace("Not listed", np.nan)
        .str.replace("%", "")
        .astype(float)
    )
    df_beer["score"] = (
        df_beer["score"]
        .replace("Needs more ratings", np.nan)
        .astype(str)
        .str.replace("Ranked .+", "")
        .astype(float)
    )
    df_beer["pdev"] = df_beer["pdev"].str.replace("%", "").astype(float)
    df_beer = df_beer.drop(columns=["date_rated", "date_added"])
    df_beer = df_beer.dropna()

    df_comment = pd.DataFrame(comment).rename(
        columns={
            "comment_beer_number": "beer_id",
            "comment_score": "score",
            "comment_rdev": "rdev",
        }
    )
    df_comment["rdev"] = (
        df_comment["rdev"].str.replace(r"[+-]|rDev ", "").str.replace("%", "")
    )
    df_comment = df_comment.drop(columns=["date"])
    df_comment = df_comment.dropna()

    df_style = pd.DataFrame(style).rename(
        columns={
            "style_name": "id",
            "style_description": "description",
            "style_abv": "abv",
            "style_ibu": "ibu",
            "style_glassware": "glassware",
        }
    )
    df_style["abv_from"] = (
        df_style["abv"].str.replace("(-|–)[0-9.]+%", "").astype(float)
    )
    df_style["abv_to"] = (
        df_style["abv"]
        .str.replace("[0-9.]+(-|–)", "")
        .str.replace("%", "")
        .astype(float)
    )
    df_style["ibu_from"] = (
        df_style["ibu"].str.replace("(-|–)[0-9]+", "").astype(int)
    )
    df_style["ibu_to"] = (
        df_style["ibu"].str.replace("[0-9]+(-|–)", "").astype(int)
    )
    df_style = df_style.dropna()

    adjusted_location = df_location.to_dict(orient="records")
    adjusted_brewery = df_brewery.to_dict(orient="records")
    adjusted_beer = df_beer.to_dict(orient="records")
    adjusted_comment = df_comment.to_dict(orient="records")
    adjusted_style = df_style.to_dict(orient="records")

    return (
        adjusted_location,
        adjusted_brewery,
        adjusted_beer,
        adjusted_comment,
        adjusted_style,
    )


def classify(beer):
    df_beer = pd.DataFrame(beer)
    df_beer["count_wants"] = pd.cut(
        df_beer["count_wants"],
        bins=10,
    )
    df_beer["count_gots"] = pd.cut(
        df_beer["count_gots"],
        bins=10,
    )
    df_beer["has_description"] = df_beer["description"].isna()
    df_beer["score"] = pd.cut(
        df_beer["score"],
        bins=10
    )
    df_beer["pdev"] = pd.cut(
        df_beer["pdev"],
        bins=10,
    )

    adjusted_beer = df_beer.to_dict(orient="records")

    return adjusted_beer


# run scrapper & transform
def run_scrapper():
    # scrap
    scraper = BeerScraper(cookies=COOKIES, pages=20)
    brewery, beer, comment, style = scraper.start_scraping()

    # normalize
    brewery, location = normalize(brewery)

    # export raw
    pd.DataFrame(brewery).to_csv(os.path.join(FOLDER, "brewery_raw.csv"))
    pd.DataFrame(beer).to_csv(os.path.join(FOLDER, "beer_raw.csv"))
    pd.DataFrame(comment).to_csv(os.path.join(FOLDER, "comment_raw.csv"))
    pd.DataFrame(style).to_csv(os.path.join(FOLDER, "style_raw.csv"))
    pd.DataFrame(location).to_csv(os.path.join(FOLDER, "location_raw.csv"))

    # process
    location, brewery, beer, comment, style = process(
        location=pd.read_csv(os.path.join(FOLDER, "location_raw.csv"), thousands=",").to_dict(orient="records"),
        brewery=pd.read_csv(os.path.join(FOLDER, "brewery_raw.csv"), thousands=",").to_dict(orient="records"),
        beer=pd.read_csv(os.path.join(FOLDER, "beer_raw.csv"), thousands=",").to_dict(orient="records"),
        comment=pd.read_csv(os.path.join(FOLDER, "comment_raw.csv"), thousands=",").to_dict(orient="records"),
        style=pd.read_csv(os.path.join(FOLDER, "style_raw.csv"), thousands=",").to_dict(orient="records"),
    )
    # classify
    beer = classify(beer)

    # export
    pd.DataFrame(brewery).to_csv(os.path.join(FOLDER, "brewery.csv"))
    pd.DataFrame(beer).to_csv(os.path.join(FOLDER, "beer.csv"))
    pd.DataFrame(comment).to_csv(os.path.join(FOLDER, "comment.csv"))
    pd.DataFrame(style).to_csv(os.path.join(FOLDER, "style.csv"))
    pd.DataFrame(location).to_csv(os.path.join(FOLDER, "location.csv"))
