import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm


class BeerScraper:
    def __init__(self, cookies, pages=1):
        self.base_url = "https://www.beeradvocate.com"
        self.start_urls = [
            f"{self.base_url}/place/list/?start={i * 20 + 500}&&sort=numbeers"
            for i in range(pages)
        ]
        self.style_url = f"{self.base_url}/beer/styles"
        self.cookies = cookies

    def parse_brewery_page(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("#ba-content tr")
        page = []
        beer = []
        comments = []

        for row in tqdm(
            [
                row
                for row in rows[1:]
                if row.select("a")[0]["href"].startswith("/beer/")
            ],
            desc="Brewery",
        ):
            brewery = row.select("a")[0]["href"]
            brewery_info, beer_info, comments_info = self.parse_brewery(
                f"{self.base_url}{brewery}"
            )
            page.append(brewery_info)
            beer.extend(beer_info)
            comments.extend(comments_info)
        return page, beer, comments

    def parse_brewery(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        stats = soup.select("#item_stats dd")

        brewery_info = {
            "brewery_name": soup.select_one("h1").text.strip(),
            "brewery_number": response.url.split("/")[-2],
            "brewery_beer_number": stats[1].text.strip(),
            "brewery_beer_ratings": stats[2].text.strip(),
            "brewery_beer_score": stats[0].text.strip(),
        }
        location = [el.text.strip() for el in soup.select("#info_box a")]
        brewery_info["brewery_city"] = location[0]
        brewery_info["brewery_country"] = location[1]
        if location[3] == "map":
            brewery_info["brewery_country"] = location[2]
            brewery_info["brewery_province"] = location[1]

        beer_info = []
        comments_info = []

        for beer_url in tqdm(
            [
                el.get("href")
                for el in soup.select("td.hr_bottom_light a")
                if el.get("href").startswith("/beer/profile")
            ],
            desc="Beers",
        ):
            beer, comments = self.parse_beer(f"{self.base_url}{beer_url}")
            beer_info.append(beer)
            comments_info.extend(comments)

        return brewery_info, beer_info, comments_info

    def parse_beer(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        beer_info = {}
        url_text = response.url
        url_list = url_text.split("/")
        beer_info["brewery_number"] = url_list[-3]
        beer_info["beer_number"] = url_list[-2]
        beer_info["brewery_name"] = soup.select_one("h1 span").text.strip()
        beer_info["beer_name"] = (
            soup.select_one("h1")
            .text.strip()
            .replace(beer_info["brewery_name"], "")
        )

        stats = soup.select("dd.beerstats")

        beer_info["beer_style"] = stats[3].text.strip()
        beer_info["beer_abv"] = stats[4].text.strip()
        beer_info["beer_score"] = stats[5].text.strip()
        beer_info["beer_avg"] = stats[6].text.split("|")[0].strip()
        beer_info["beer_pDev"] = stats[6].text.split("| pDev:")[1].strip()
        beer_info["beer_reviews"] = stats[7].text.strip()
        beer_info["beer_ratings"] = stats[8].text.strip()
        beer_info["beer_status"] = stats[9].text.strip()
        beer_info["beer_rated"] = stats[10].text.strip()
        beer_info["beer_added"] = stats[11].text.split("by")[0].strip()
        beer_info["beer_added_user"] = stats[11].text.split("by")[1].strip()
        beer_info["beer_wants"] = stats[12].text.strip()
        beer_info["beer_gots"] = stats[13].text.strip()

        description = (
            soup.find("div", id="box_wrapper").find_next_sibling("div").text
        )
        if not description.startswith("\nNo description / notes."):
            beer_info["beer_description"] = description.split(
                "Photo uploaded by"
            )[0].strip()

        comments_info = [
            self.parse_comment(comment=comment, beer=beer_info)
            for comment in soup.select("#rating_fullview_content_2")
            if comment.select_one("span.BAscore_norm")
        ]
        return beer_info, comments_info

    def parse_comment(self, comment, beer):
        comment_item = {
            "comment_beer_number": beer["beer_number"],
            "comment_score": comment.select_one(
                "span.BAscore_norm"
            ).text.strip(),
            "comment_rdev": (
                comment.select_one("span.BAscore_norm")
                .find_next_sibling("span")
                .find_next_sibling("span")
                .text.strip()
            ),
        }
        scores = (
            comment.select_one("span.BAscore_norm")
            .find_next_sibling("span")
            .find_next_sibling("span")
            .find_next_sibling("span")
            .text.strip()
        )

        look = re.search(r"look: ([0-9\\.]*) \|", scores)
        if look:
            comment_item["look"] = look.group(1)

        smell = re.search(r"smell: ([0-9\\.]*) \|", scores)
        if smell:
            comment_item["smell"] = smell.group(1)

        taste = re.search(r"taste: ([0-9\\.]*) \|", scores)
        if taste:
            comment_item["taste"] = taste.group(1)

        feel = re.search(r"feel: ([0-9\\.]*) \|", scores)
        if feel:
            comment_item["feel"] = feel.group(1)

        overall = re.search(r"overall: ([0-9\\.]*)", scores)
        if overall:
            comment_item["overall"] = overall.group(1)

        comment_item["comment"] = (
            comment.select_one("span.BAscore_norm")
            .find_next_sibling("div")
            .text
        )

        comment_item["username"] = comment.select_one(
            "div#rating_fullview_content_2 span.muted a.username"
        ).text.strip()
        comment_item["date"] = comment.select(
            "div#rating_fullview_content_2 span.muted a"
        )[-1].text.strip()
        return comment_item

    def parse_style_page(self):
        response = requests.get(self.style_url, cookies=self.cookies)
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("#ba-content li a")

        style = []

        for row in tqdm(
            [row for row in rows if row["href"].startswith("/beer/styles")],
            desc="Styles",
        ):
            style_url = row["href"]
            style_info = self.parse_style(f"{self.base_url}{style_url}")
            style.append(style_info)
        return style

    def parse_style(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        style_info = {"style_name": soup.select_one("h1").text.strip()}
        style = soup.select_one("#ba-content").find_next("div").text
        style_info["style_description"] = style.split("ABV")[0].strip()
        style_info["style_abv"] = re.search(
            r"ABV: ([0-9\\.\-–%]*)", style
        ).group(1)
        style_info["style_ibu"] = re.search(
            r"IBU: ([0-9\\.\-–]*)", style
        ).group(1)
        style_info["style_glassware"] = re.search(
            r"Glassware: (.*)\n", style
        ).group(1)

        return style_info

    def start_scraping(self):
        parsed_brewery, parsed_beer, parsed_comments = [], [], []
        for url in self.start_urls:
            brewery, beer, comments = self.parse_brewery_page(url)
            parsed_brewery.extend(brewery)
            parsed_beer.extend(beer)
            parsed_comments.extend(comments)
        parsed_styles = self.parse_style_page()
        return parsed_brewery, parsed_beer, parsed_comments, parsed_styles
