import requests
from lxml import etree
from parsers.base_parser import BaseParser
from parsers.helpers import normalize_polish

class LocationParser(BaseParser):
    PARSER_TYPE = 'location'
    SEED_URL = 'https://pl.escort.club/anonse/towarzyskie/poland/'
    CITIES_URL = 'https://pl.escort.club/getCity.php'
    CITIES_PAYLOAD = {
        'state_id': None,
        'selected': False,
        'front': 1,
        'search': 1,
    }
    XPATHS = {
        'provinces': '//select[@name="province"]/option[position() > 1]',
        'cities': '//option[position() > 1]',
    }
    
    def __init__(self, cookies, logger):
        self.cookies = cookies
        self.logger = logger
    
    def run(self):
        self.logger.info("Started parsing locations...")
        self.save_to_results(self.parse_locations())
        self.logger.info("Location parsing completed and results saved.")

    
    def parse_locations(self):
        locations = []
        for province in self.parse_provinces():
            province['cities'] = self.parse_cities(province)
            locations.append(province)
        return locations

    def parse_provinces(self):
        response = requests.get(LocationParser.SEED_URL, cookies=self.cookies)
        html = etree.HTML(response.text)
        return LocationParser.create_provinces(html)

    @staticmethod
    def create_provinces(html):
        for province_node in html.xpath(LocationParser.XPATHS['provinces']):
            yield LocationParser.create_province_dict(province_node)

    @staticmethod
    def create_province_dict(province_node):
        name = province_node.xpath('./text()')[0]
        return {
            'id': province_node.xpath('./@value')[0],
            'name': name,
            'slug': normalize_polish(name),
        }
    
    def parse_cities(self, province):
        response = requests.post(LocationParser.CITIES_URL, 
                                 data={**LocationParser.CITIES_PAYLOAD, 'state_id': province['id']}, 
                                 cookies=self.cookies)
        html = etree.HTML(response.text)
        return LocationParser.create_cities(html)
    
    @staticmethod
    def create_cities(html):
        return [LocationParser.create_city_dict(city_node) for city_node in html.xpath(LocationParser.XPATHS['cities'])]
        
    @staticmethod
    def create_city_dict(city_node):
        name = city_node.xpath('./text()')[0]
        return {
            'id': city_node.xpath('./@value')[0],
            'name': name,
            'slug': normalize_polish(name),
        }   