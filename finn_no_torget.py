# -*- coding: utf-8 -*-

import mechanicalsoup as ms
import notify  # Local module, included in $PYTHONPATH
import traceback
from urllib.parse import urljoin
from scrape_tools import write_with_timestamp, compare_results, i_o_setup, alert_write_new, get_ids

PUSH_NOTIFICATION = True
EMAIL_NOTIFICATION = False

MAX_NOT_ENTRIES = 4
MAX_PAGES = 10

BROWSER = ms.StatefulBrowser()

SEARCH_URL_FILE = './in_out/search_url.in'
ADS_FILE = './in_out/ads.out'
HISTORY_FILE = './in_out/history.txt'

FINNNO_BASE_URL = 'https://www.finn.no/bap/forsale/search.html'

EMAIL = 'landsverk.vegard@gmail.com'
API_TOKEN = 'a7a4i1tr926egsttpjnydsu461y4m4'


def main():
    try:
        searches = i_o_setup(ADS_FILE, HISTORY_FILE, SEARCH_URL_FILE)
        new_ad_dicts = get_ids(searches, ADS_FILE, process_page)

        if new_ad_dicts:
            alert_write_new('Finn.no (torget)', new_ad_dicts, searches, ad_string_format,
                            push_notifications=PUSH_NOTIFICATION, email_notifications=EMAIL_NOTIFICATION,
                            output_file=HISTORY_FILE, max_notif_entries=MAX_NOT_ENTRIES, api_token=API_TOKEN)

    except Exception:
        notify.mail(EMAIL, 'Feil under kjøring av hybelskript', "{}".format(traceback.format_exc()))
        traceback.print_exc()


# Scrapes pages recursively. ID used since title (in url) might change.
def process_page(page_url, ad_dict, search, page_num):
    page = BROWSER.get(page_url).soup

    ads = page.find('div', class_='ads').findAll('article')

    for ad in ads:
        price = ad.find('div', class_='ads__unit__img__ratio__price').get_text(strip=True)

        reseller_elmnt = ad.find('div', class_='ads__unit__content__list')
        reseller = 'Betalt plassering' if not reseller_elmnt else reseller_elmnt.get_text(strip=True)

        details_elmnts = ad.find('div', class_='ads__unit__content__details').contents
        if len(details_elmnts) > 1:
            timestamp = details_elmnts[0].get_text(strip=True)
            address = details_elmnts[1].get_text(strip=True)
        else:
            address = details_elmnts[0].get_text(strip=True)
        a_link = ad.find('a', class_='ads__unit__link')

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

    next_page = page.find('a', class_='button button--pill button--has-icon button--icon-right')

    if next_page and page_num <= MAX_PAGES:
        page_num += 1
        next_url = urljoin(FINNNO_BASE_URL, next_page.attrs['href'])
        process_page(next_url, ad_dict, search, page_num)

    return ad_dict


def ad_string_format(ad_link, search_link, ad_dict):
    return f'{ad_link} – {ad_dict["price"]} ({search_link})\n{ad_dict["address"]} ({ad_dict["reseller"]})'


if __name__ == '__main__':
    main()
