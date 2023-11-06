# import json
import aiohttp
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import pandas as pd


async def fetch_html_content(url: str, session: ClientSession) -> str:
    async with session.get(url) as response:
        return await response.text()


async def get_company_data(url: str, session: ClientSession) -> dict:
    response = await fetch_html_content(url, session)
    soup = BeautifulSoup(response, 'lxml')

    company_name = soup.find(class_="header-wrap clear")
    company_ceo = soup.select_one('li:has(> em:-soup-contains("Daglig leder:"))')
    company_phone = soup.find(class_="tel addax addax-cs_ip_phone_click icon ss-phone")
    company_mobile_phone = soup.find(class_="tel addax addax-cs_ip_phone_click icon ss-cell")
    company_address = soup.select_one('ul.content.definition-list li:has(> em:-soup-contains("Adresse:"))')
    company_postal_address = soup.select_one('ul.content.definition-list li:has(> em:-soup-contains("Postadresse:"))')
    company_mail = soup.find(class_="addax addax-cs_ip_email_click icon ss-mail")
    company_website = soup.find(class_="addax addax-cs_ip_homepage_url_click icon ss-globe")

    data = {
        'company_name': company_name.find('h1').text if company_name else '',
        'company_ceo': company_ceo.find('span').text if company_ceo else '',
        'company_phone': company_phone.text if company_phone else '',
        'company_mobile_phone': company_mobile_phone.text if company_mobile_phone else '',
        'company_address': company_address.find("span").text if company_address else '',
        'company_postal_address': company_postal_address.find('span').text if company_postal_address else '',
        'company_mail': company_mail.find('span').text if company_mail else '',
        'company_website': company_website.text if company_website else ''
    }
    
    return data


async def extract_and_save_company_data(base_url: str, headers: dict) -> list:
    async with aiohttp.ClientSession(headers=headers) as session:
        current_url = base_url
        all_companies_data = []

        while current_url:
            response = await fetch_html_content(current_url, session)
            soup = BeautifulSoup(response, 'lxml')
            block_info = soup.find_all(class_="search-block-wrap")

            url_list = [f"https://www.proff.no{item.get('details')}" for item in block_info]

            task_list = [get_company_data(url, session) for url in url_list]
            companies_data = await asyncio.gather(*task_list)

            all_companies_data.extend(companies_data)

            next_page = soup.find('li', class_='next')
            if next_page:
                next_page_link = next_page.find('a')['href']
                current_url = f"https://www.proff.no{next_page_link}"
            else:
                current_url = None

        return all_companies_data


# Сохранение данных в Excel файл
def write_to_excel(data: list, filename: str) -> None:
    df = pd.DataFrame(data)
    df.columns = [
        'company_name',
        'company_ceo',
        'company_phone',
        'company_mobile_phone',
        'company_address',
        'company_postal_address',
        'company_mail',
        'company_website'
    ]
    df.to_excel(filename, index=False, engine='openpyxl')


# Сохранение данных в файл
# def write_to_json(data: list, filename: str) -> None:
#     with open(filename, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, ensure_ascii=False, indent=4)


def main():
    base_url = 'https://www.proff.no/bransjes%C3%B8k?q=Entrepren%C3%B8rer'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    data = asyncio.run(extract_and_save_company_data(base_url, headers))
    write_to_excel(data, 'companies_data.xlsx')
    # write_to_json(data, 'companies_data.json')


if __name__ == '__main__':
    main()
