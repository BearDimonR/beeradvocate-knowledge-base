# beeradvocate-knowledge-base
A simple random tree classifier with scrapper logic and neo4j as storage engine


## Basic NEO4J QUERIES
Link: http://localhost:7474/browser/

Top beer locations
```cypher
MATCH (l:Location)<-[:LOCATES]-(b:Brewery)-[:PRODUCES]->(beer:Beer)
WHERE beer.beer_avg IS NOT NULL
WITH l, AVG(beer.beer_avg) AS avgRating
RETURN l.brewery_city AS City, l.brewery_country AS Country, l.brewery_province AS Province, avgRating AS AverageRating
ORDER BY avgRating DESC
LIMIT 5
```

Top beer styles
```cypher
MATCH (style:Style)<-[:HAS_STYLE]-(beer:Beer)
WHERE beer.beer_avg IS NOT NULL
WITH style, AVG(beer.beer_avg) AS avgRating
RETURN style.style_name AS Style, avgRating AS AverageRating
ORDER BY avgRating DESC
LIMIT 5
```

Top beer locations with the biggest comments number
```cypher
MATCH (l:Location)<-[:LOCATES]-(b:Brewery)-[:PRODUCES]->(:Beer)-[:HAS_COMMENT]->(comment:Comment)
WITH l, COUNT(comment) AS numComments
WHERE numComments > 0
RETURN l.brewery_city AS City, l.brewery_country AS Country, l.brewery_province AS Province, numComments AS NumberOfComments
ORDER BY numComments DESC
LIMIT 5
```