import requests
from parsers.base_parser import BaseParser
from lxml import etree
import copy


class RankingParser(BaseParser):
    PARSER_TYPE = "ranking"
    XPATHS = {
        "next_page": '//ul[@class="ads-navigation"]//a[@class="next"]',
        "advertisements": '//section[contains(@class, "content")]//a[contains(@href, "anons")]',
        "name": './/span[@class="item-name"]',
        "img": './/img[contains(@class, "lazy")]/@data-src',
        "stats": './/span[@class="item-stats"]',
    }
    RANKING_URL = "https://pl.escort.club/anonse/towarzyskie/{city_slug}/{page}?province={province_id}"
    PAGE_LIMIT = 50

    def __init__(self, location_data, cookies, logger=None):
        self.location_data = location_data
        self.cookies = cookies
        self.logger = logger
        self.failed_locations = []

    def run(self):
        self.logger.info("Started parsing rankings...")
        self.save_to_results(self.parse_location_rankings())
        self.save_to_results(self.failed_locations, error=True)
        self.logger.info("Ranking parsing completed and results saved.")

    # Iterate over all provinces
    def parse_location_rankings(self):
        self.location_rankings = []
        for province in self.location_data:
            self.process_province(province)
        return self.location_rankings

    def process_province(self, province):
        try:
            province_rankings = {**province, "cities": []}
            province_rankings["cities"] = RankingParser.parse_province_rankings(
                self, province
            )
            self.location_rankings.append(province_rankings)
        except Exception as e:
            self.logger.error(
                f"Error occurred while processing province {province['name']}: {e}"
            )
            self.failed_locations.append(province)

    # Iterate over all cities in a province
    def parse_province_rankings(self, province):
        cities = []
        for city in province["cities"]:
            city = copy.deepcopy(city)

            self.logger.info(
                f"Parsing advertisements for {province['name']} - {city['name']}"
            )
            city["rankings"] = self.parse_city_rankings(province, city)
            self.logger.info(f"Total advertisements found: {len(city['rankings'])}")
            self.logger.info(f"Done for {province['name']} - {city['name']}")
            cities.append(city)
        return cities

    def parse_city_rankings(self, province, city):
        page_number = 1
        advertisements = []
        while page_number < RankingParser.PAGE_LIMIT:
            html = self.request_page(province, city, page_number)
            advertisements.extend(
                RankingParser.create_advertisements(html, page_number)
            )
            if not RankingParser.check_next_page(html):
                break
            page_number += 1
        return advertisements

    def request_page(self, province, city, page_number):
        page_slug = f"page{page_number}.html" if page_number > 1 else ""
        response = requests.get(
            RankingParser.RANKING_URL.format(
                city_slug=city["slug"],
                page=page_slug,
                province_id=province["id"],
            ),
            cookies=self.cookies,
        )
        return etree.HTML(response.text)

    @staticmethod
    def create_advertisements(html, page_number):
        advertisements = []
        for index, node in enumerate(
            html.xpath(RankingParser.XPATHS["advertisements"]), start=1
        ):
            advertisements.append(
                RankingParser.create_advertisement_dict(node, index, page_number)
            )
        return advertisements

    @staticmethod
    def create_advertisement_dict(node, index, page_number):
        return {
            "url": node.xpath("./@href")[0],
            "name": node.xpath(RankingParser.XPATHS["name"])[0].text.strip(),
            "img": node.xpath(RankingParser.XPATHS["img"])[0],
            "stats": node.xpath(RankingParser.XPATHS["stats"])[0].text.strip(),
            "position": index,
            "page_number": page_number,
        }

    @staticmethod
    def check_next_page(html):
        return bool(html.xpath(RankingParser.XPATHS["next_page"]))
