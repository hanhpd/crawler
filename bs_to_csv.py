from bs4 import BeautifulSoup
import datetime
from tinydb import TinyDB, Query
import urllib3
import xlsxwriter
import json
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# https://tiki.vn/search?q=<keyword>
url = 'https://tiki.vn/'
total_added = 0
numb_page = 0
def get_sub_url(types):
    product_links = []
    for type in types:
        product_link = (type.find('span', class_='text').string, type.a['href'])
        product_links.append(product_link)
    return product_links
def make_soup(url):
    # http = urllib3.ProxyManager('https://101.96.112.66:8080')
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    return BeautifulSoup(r.data,'lxml')

def clean_money(amt):
    return amt.replace(".","")

def get_data_all(product, link, data):
    global numb_page
    sub_soup = make_soup(link)
    numb = sub_soup.find('div', class_='product-box no-mg').div.h4.string.split()[0]
    numb_page = int(int(numb) / 48) + 2
    for i in range(1, numb_page):
        get_link = link + '&order=top_seller&page=' + str(i)
        if not get_data(product, get_link, data):
            break

def get_data(product, link, data):
    global total_added
    success = False
    sub_soup = make_soup(link)
    results = sub_soup.find_all('div', class_='product-item')

    for result in results:
        data['index'].append(total_added)
        total_added += 1
        data['product'].append(product)
        data['product_item_id'].append(result['data-id'])
        data['name'].append(result['data-title'])
        try:
            data['brand'].append(result['data-brand'])
        except (AttributeError, KeyError) as ex:
            data['brand'].append('NA')

        data['final_price'].append(result['data-price'])
        try:
            data['price_regular'].append(clean_money(result.find('span', class_='price-regular').string.strip('đ')))
        except (AttributeError, KeyError) as ex:
            data['price_regular'].append(result['data-price'])
        try:
            data['sale_off'].append(result.find('span', class_='sale-tag sale-tag-square').string.strip())
        except (AttributeError, KeyError) as ex:
            data['sale_off'].append('0')
        try:
            data['rate'].append(result.a.find('div', class_='review-wrap').p.span.span['style'].strip('width:'))
        except (AttributeError, KeyError) as ex:
            data['rate'].append('0')

        tmp = result.find('p', class_='review').string.strip('(').split()[0]
        if tmp.isdigit():
            data['numb_review'].append(tmp)
        else:
            data['numb_review'].append('0')

        try:
            data['status'].append(result.find('p', class_='notify notify-warning').string)
        except (AttributeError, KeyError) as ex:
            data['status'].append('còn hàng')
        try:
            data['delivery'].append(result.find('p', class_='past-delivery').text.strip('\n'))
        except (AttributeError, KeyError) as ex:
            data['delivery'].append('Không giao hàng nhanh')
        data['webpage'].append(result.a['href'])
        data['create_date'].append(datetime.datetime.now().strftime("%H:%M:%S      %d/%m/%Y"))
        success = True

    print("Web : ", link)
    print("Added ", total_added, " item")
    return success

def soup_process(url):
    data = {
        'index': [],
        'product' : [],
        'product_item_id': [],
        'name': [],
        'brand': [],
        'final_price': [],
        'price_regular': [],
        'sale_off': [],
        'rate': [],
        'numb_review': [],
        'status': [],
        'delivery': [],
        'webpage': [],
        'create_date': []
    }

    soup = make_soup(url)
    types = soup.find('div', class_="home-page").main.div.ul.find_all('li')
    product_links = get_sub_url(types, )
    for product_link in product_links:
        product = list(product_link)[0]
        link = list(product_link)[1]
        get_data_all(product, link, data)

    return data

def make_csv(data):
    df = pd.DataFrame(data)
    df.to_csv('tiki.csv', index = False, encoding='utf-8-sig')
def main(url):
    # while url:
    data = soup_process(url)
        # nextlink = soup.find("link", rel="next")
        #
        # url = False
        # if (nextlink):
        #     url = nextlink['href']

    make_csv(data)

main(url)