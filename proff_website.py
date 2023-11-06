import json
import requests
from bs4 import BeautifulSoup

base_url = 'https://www.proff.no/bransjes%C3%B8k?q=Entrepren%C3%B8rer'
count = 1

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

while base_url:
    response = requests.get(base_url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    block_info = soup.find_all(class_="search-block-wrap")

    url_list = []
    for item in block_info:
        details = item.get("details")
        url_details = f"https://www.proff.no" + details
        url_list.append(url_details)

    companies_data = []
    for url in url_list:
        response = requests.get(url, headers=headers).text
        company_soup = BeautifulSoup(response, 'lxml')

        company_name = company_soup.find(class_="header-wrap clear")
        company_phone = company_soup.find(class_="tel addax addax-cs_ip_phone_click icon ss-phone")
        company_mobile_phone = company_soup.find(class_="tel addax addax-cs_ip_phone_click icon ss-cell")
        company_address = company_soup.find(class_="map-address")
        company_mail = company_soup.find(class_="addax addax-cs_ip_email_click icon ss-mail")
        company_website = company_soup.find(class_="addax addax-cs_ip_homepage_url_click icon ss-globe")

        data = {
            'company_name': company_name.find('h1').text if company_name else '',
            'company_phone': company_phone.text if company_phone else '',
            'company_mobile_phone': company_mobile_phone.text if company_mobile_phone else '',
            'company_address': company_address.find("span").text if company_address else '',
            'company_mail': company_mail.find('span').text if company_mail else '',
            'company_website': company_website.text if company_website else ''
        }

        print(f'{count}. {data["company_name"]}')
        companies_data.append(data)
        count += 1

    next_page = soup.find('li', class_='next')
    if next_page:
        next_page_link = next_page.find('a')['href']
        base_url = f"https://www.proff.no{next_page_link}"
    else:
        base_url = None

    with open('data.json', 'a', encoding='utf-8') as json_file:
        json.dump(companies_data, json_file, ensure_ascii=False, indent=4)
