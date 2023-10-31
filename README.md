# beeradvocate-knowledge-base
A simple random tree classifier with scrapper logic and neo4j as storage engine

## Scrapper data processing
1. Split brewery with location (normalization)
2. Filtered invalid values/parsed others ("noice" removal)
3. Classified numerical columns into categorical ones


## Basic NEO4J QUERIES
Link: http://localhost:7474/browser/

Top beer locations
```cypher
MATCH (l:Location)<-[:LOCATES]-(b:Brewery)-[:PRODUCES]->(beer:Beer)
WHERE beer.avg IS NOT NULL
WITH l, AVG(beer.avg) AS avgRating
RETURN l.city AS City, l.country AS Country, l.province AS Province, avgRating AS AverageRating
ORDER BY avgRating DESC
LIMIT 5
```

Top beer styles
```cypher
MATCH (style:Style)<-[:HAS_STYLE]-(beer:Beer)
WHERE beer.avg IS NOT NULL
WITH style, AVG(beer.avg) AS avgRating
RETURN style.name AS Style, avgRating AS AverageRating
ORDER BY avgRating DESC
LIMIT 5
```

Top beer locations with the biggest comments number
```cypher
MATCH (l:Location)<-[:LOCATES]-(b:Brewery)-[:PRODUCES]->(:Beer)-[:HAS_COMMENT]->(comment:Comment)
WITH l, COUNT(comment) AS numComments
WHERE numComments > 0
RETURN l.city AS City, l.country AS Country, l.province AS Province, numComments AS NumberOfComments
ORDER BY numComments DESC
LIMIT 5
```

### Building expert rule-based model

We build a random forest classifier to classify 10 bins of beer score.
Also, we visualized trees to make logic clear and made a simple demo