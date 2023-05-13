#!/usr/bin/env python3

from urllib.parse import urljoin
from scrape_tools import scrape_site


FINNNO_BASE_URL = 'https://www.finn.no/bap/forsale/search.html'
PUSHOVER_TOKEN = 'a7a4i1tr926egsttpjnydsu461y4m4'


def main():
    scrape_site(get_elements, get_attrs, get_next_page, 'Finn.no (torget)', ad_string_format, 
                pushover_token=PUSHOVER_TOKEN)


def get_elements(page):
    return page.find('div', class_='ads').findAll('article')


def get_next_page(page, _page_url):
    next_page = page.find('a', class_='button button--pill button--has-icon button--icon-right')
    if not next_page:
        return None
    return urljoin(FINNNO_BASE_URL, next_page.attrs['href'])


def get_attrs(ad_element, ad_dict, search):
    price = ad_element.find('div', class_='ads__unit__img__ratio__price').get_text(strip=True)

    reseller_elmnt = ad_element.find('div', class_='ads__unit__content__list')
    reseller = 'Betalt plassering' if not reseller_elmnt else reseller_elmnt.get_text(strip=True)

    details_elmnts = ad_element.find('div', class_='ads__unit__content__details').contents
    if len(details_elmnts) > 1:
        timestamp = details_elmnts[0].get_text(strip=True)
        address = details_elmnts[1].get_text(strip=True)
    else:
        address = details_elmnts[0].get_text(strip=True)

    a_link = ad_element.find('a', class_='ads__unit__link')

    ad_id = a_link.attrs['id']
    href = a_link.attrs['href']
    title = a_link.get_text(strip=True)

    ad_dict[ad_id] = dict(
        href=href,
        title=title,
        address=address,
        price=price,
        search=search,
        reseller=reseller
    )

    return ad_dict


def ad_string_format(ad_link, search_link, ad_dict):
    return f'{ad_link} – {ad_dict["price"]} ({search_link})\n{ad_dict["address"]} ({ad_dict["reseller"]})'


if __name__ == '__main__':
    main()
