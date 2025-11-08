import requests

cookies = {
    'escortsession': 't9paatr9nhebv18gciqor59qo5',
    'warning': '1',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,ru-RU;q=0.6,ru;q=0.5',
    'priority': 'u=0, i',
    'referer': 'https://pl.escort.club/anonse/towarzyskie/poland/?province=&filter_price_type=&filter_price=0%3B25000&filter_age=18%3B100&filter_weight=30%3B200&filter_height=100%3B220&filter_breasts=0%3B8&breasts_type=&hair_colors=&sexual_orientation=&searchlang=&zodiac_sign=&q=',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
}

params = {
    'province': '12',
}

response = requests.get('https://pl.escort.club/anonse/towarzyskie/krakow/', params=params, cookies=cookies, headers=headers)

with open('response.html', 'w') as file:
    file.write(response.text)