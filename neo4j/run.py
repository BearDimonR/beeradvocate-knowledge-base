import os

import pandas as pd

from constants import FOLDER, NEO4J_PASSWORD, NEO4J_USERNAME, NEO4J_URI
from neo4j.neo4j_data_manager import Neo4jDataManager


# refresh neo4j database
def run_refresh_database():
    df_locations = pd.read_csv(os.path.join(FOLDER, "location.csv"))
    df_breweries = pd.read_csv(os.path.join(FOLDER, "brewery.csv"))
    df_beers = pd.read_csv(os.path.join(FOLDER, "beer.csv"))
    df_comments = pd.read_csv(os.path.join(FOLDER, "comment.csv"))
    df_styles = pd.read_csv(os.path.join(FOLDER, "style.csv"))

    # make arrays
    locations = df_locations.to_dict(orient="records")
    breweries = df_breweries.to_dict(orient="records")
    beers = df_beers.to_dict(orient="records")
    styles = df_styles.to_dict(orient="records")
    comments = df_comments.to_dict(orient="records")

    # refresh & push to DB
    data_manager = Neo4jDataManager(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    data_manager.clear_database()

    location_nodes = data_manager.create_nodes("Location", locations)
    brewery_nodes = data_manager.create_nodes("Brewery", breweries)
    beer_nodes = data_manager.create_nodes("Beer", beers)
    style_nodes = data_manager.create_nodes("Style", styles)
    comment_nodes = data_manager.create_nodes("Comment", comments)

    data_manager.create_relationships(
        brewery_nodes,
        "brewery_location_id",
        location_nodes,
        "location_id",
        "LOCATES",
    )
    data_manager.create_relationships(
        brewery_nodes,
        "brewery_number",
        beer_nodes,
        "brewery_number",
        "PRODUCES",
    )
    data_manager.create_relationships(
        beer_nodes, "beer_style", style_nodes, "style_name", "HAS_STYLE"
    )
    data_manager.create_relationships(
        beer_nodes,
        "beer_number",
        comment_nodes,
        "comment_beer_number",
        "HAS_COMMENT",
    )
