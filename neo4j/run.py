import os

import pandas as pd

from constants import FOLDER
from neo4j_data_manager import Neo4jDataManager


# refresh neo4j database
def run_refresh_database():
    # process scrapped_data
    df_breweries = pd.read_csv(os.path.join(FOLDER, "brewery.csv"))
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

    df_beers = pd.read_csv(os.path.join(FOLDER, "beer"))
    df_comments = pd.read_csv(os.path.join(FOLDER, "comment"))
    df_styles = pd.read_csv(os.path.join(FOLDER, "style"))

    # make arrays
    locations = df_locations.to_dict(orient="records")
    breweries = df_breweries.to_dict(orient="records")
    beers = df_beers.to_dict(orient="records")
    styles = df_styles.to_dict(orient="records")
    comments = df_comments.to_dict(orient="records")

    # push to DB
    data_manager = Neo4jDataManager(
        "bolt://localhost:7687", "your_username", "your_password"
    )

    location_nodes = data_manager.create_nodes("Location", locations)
    brewery_nodes = data_manager.create_nodes("Brewery", breweries)
    beer_nodes = data_manager.create_nodes("Beer", beers)
    style_nodes = data_manager.create_nodes("Style", styles)
    comment_nodes = data_manager.create_nodes("Comment", comments)
    #
    # data_manager.create_relationships(beer_nodes, "LOCATES", location_nodes)
    # data_manager.create_relationships(brewery_nodes, "PRODUCES", beer_nodes)
    # data_manager.create_relationships(beer_nodes, "HAS_STYLE", style_nodes)
    # data_manager.create_relationships(beer_nodes, "HAS_COMMENT", comment_nodes)
