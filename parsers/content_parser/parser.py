import requests
from parsers.base_parser import BaseParser
from lxml import etree
import os
import json
from datetime import datetime, timezone
import pdb

from parsers.location_parser.parser import LocationParser


class ContentParser(BaseParser):
    CHUNK_SIZE = 100
    PARSER_TYPE = "content"
    XPATHS = {
        "title": '//div[contains(@class, "content-name")]//h1',
        "description": '//div[contains(@class, "content-desc")]//div[@id="PL"]',
        "price_template": '//div[contains(@class, "prices")]//div[contains(text(), "{keyword}")]/following-sibling::div[1]',
        "images": '//div[@class="galleryContainer"]//img/@src',
        "stat_template": "//div[contains(@class, 'stat-elem')]//div[contains(text(), '{keyword}')]/following-sibling::div[1]",
    }
    STATS_KEYWORDS = {
        "age": "Wiek",
        "height": "Wzrost",
        "weight": "Waga",
        "wzrost": "Wzrost",
        "breasts": "Biust",
        "eyes": "Oczy",
        "hair": "Włosy",
        "languages": "Języki",
    }
    PRICE_KEYWORDS = {
        "1_hour": "1 godz",
        "noc": "Noc",
        "30_min": "0,5 godz",
        "2_hours": "2 godz",
        "15_min": "15 min",
    }

    def __init__(self, advertisement_urls, cookies, logger, batch_num=1):
        self.advertisement_urls = advertisement_urls
        self.cookies = cookies
        self.logger = logger
        self.batch_num = batch_num
        self.session = requests.Session()
        self.result_filepath = self.create_result_filepath()

    def run(self):
        self.logger.info("Started parsing advertisements content...")
        self.parse_advertisements()
        self.logger.info("Finished parsing advertisements content.")

    def parse_advertisements(self):
        advertisements = []
        try:
            for index, url in enumerate(self.advertisement_urls):
                advertisements.append(self.parse_advertisement(url))
                if (index + 1) % ContentParser.CHUNK_SIZE == 0:
                    self.save_chunk(
                        advertisements, first=(index + 1 == ContentParser.CHUNK_SIZE)
                    )
        except Exception as e:
            self.logger.error(f"Error occurred while parsing advertisements: {e}")
        self.save_chunk(advertisements, last=True)

    def save_chunk(self, buffer, first=False, last=False):
        mode = "a" if os.path.exists(self.result_filepath) else "w"
        with open(self.result_filepath, mode, encoding="utf-8", newline="\n") as file:
            if first:
                file.write("[\n")
            elif buffer:
                file.write(",\n")

            for index, item in enumerate(buffer):
                json.dump(item, file, ensure_ascii=False)
                is_last_item_in_chunk = index == len(buffer) - 1
                if not is_last_item_in_chunk:
                    file.write(",\n")
                else:
                    # if more chunks are expected, do not end with a newline here;
                    # the next chunk will prepend ",\n" to attach directly.
                    if last:
                        file.write("\n")

            if last:
                file.write("]\n")
        buffer.clear()

    def parse_advertisement(self, url):
        html = self.request_advertisement_page(url)
        return ContentParser.create_advertisement_dict(html, url)

    def request_advertisement_page(self, url):
        response = self.session.get(url, cookies=self.cookies)
        html = etree.HTML(response.text)
        del response
        return html

    @staticmethod
    def create_advertisement_dict(html, url):
        price_stats = ContentParser.template_keywords(
            ContentParser.PRICE_KEYWORDS, html, ContentParser.XPATHS["price_template"]
        )
        quality_stats = ContentParser.template_keywords(
            ContentParser.STATS_KEYWORDS, html, ContentParser.XPATHS["stat_template"]
        )
        title_nodes = html.xpath(ContentParser.XPATHS["title"])
        desc_nodes = html.xpath(ContentParser.XPATHS["description"])
        images = html.xpath(ContentParser.XPATHS["images"]) or []

        title = title_nodes[0].text.strip() if title_nodes else None
        description = desc_nodes[0].text.strip() if desc_nodes else None

        return {
            "url": url,
            "title": title,
            "description": description,
            "images": images,
            "qualities": quality_stats,
            "prices": price_stats,
        }

    @staticmethod
    def template_keywords(template_dict, html, template_xpath):
        result = {}
        for key, keyword in template_dict.items():
            xpath = template_xpath.format(keyword=keyword)
            value = html.xpath(xpath)
            result[key] = value[0].text.strip() if value else None
        return result

    def create_result_filepath(self) -> str:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
        filename = f"{date}_{self.PARSER_TYPE}_{self.batch_num}.json"
        return os.path.join(
            BaseParser.results_directory_path(), f"{self.PARSER_TYPE}_results", filename
        )
