from bs4 import BeautifulSoup
import datetime
from tinydb import TinyDB, Query
import urllib3
import xlsxwriter
import json
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# https://tiki.vn/search?q=<keyword>
url = 'https://tiki.vn/do-choi-me-be/c2549'
total_added = 0
def make_soup(url):
    http = urllib3.ProxyManager('https://101.96.112.66:8080')
    r = http.request("GET", url)
    return BeautifulSoup(r.data,'lxml')

def main(url):
    global total_added
    db = TinyDB("db-example.json")
    db.purge()

    # while url:
    print("Web Page: ", url)
    soup = soup_process(url, db)
        # nextlink = soup.find("link", rel="next")
        #
        # url = False
        # if (nextlink):
        #     url = nextlink['href']

    print("Added ",total_added)

    make_excel(db)

def soup_process(url, db):
    global total_added
    rec = {
        'dataId' : '0',
        'name' : "NA",
        'brand' : "NA",
        'final-price' : '0',
        'price-regular' : '0',
        'saleoff' : '0',
        'rate' : '0',
        'review' : '0',
        'delivery' : "NA",
        'webpage' : "NA",
        'createdt' : "NA"
    }
    soup = make_soup(url)
    results = soup.find_all('div', class_='product-item')

    for result in results:
        rec['dataId'] = result['data-id']
        rec['name'] =  result['data-title']
        try:
            rec['brand'] = result['data-brand']
        except (AttributeError, KeyError) as ex:
            rec['brand'] = "NA"

        rec['final-price'] = result['data-price']

        try:
            rec['price-regular'] = clean_money(result.find('span', class_='price-regular').string.strip('đ'))
        except (AttributeError, KeyError) as ex:
            rec['price-regular'] = rec['final-price']

        try:
            rec['saleoff'] = result.find('span', class_='sale-tag sale-tag-square').string.strip()
        except (AttributeError, KeyError) as ex:
            rec['saleoff'] = '0'

        try:
            rec['rate'] = result.a.find('div', class_='review-wrap').p.span.span['style'].strip('width:')
        except (AttributeError, KeyError) as ex:
            rec['rate'] = '0'
        rec['review'] = result.find('p', class_='review').string.strip('(').split()[0]
        if rec['review'].isdigit() == 0:
            rec['review'] = '0'
        try:
            rec['delivery'] = result.find('p', class_='past-delivery').text.strip('\n')
        except (AttributeError, KeyError) as ex:
            rec['delivery'] = "không giao hàng nhanh"
        rec['webpage'] =  result.a['href']
        rec['createdt'] = datetime.datetime.now().strftime("%H:%M:%S      %d/%m/%Y")
        print(datetime.datetime.now().strftime("%H:%M:%S      %d/%m/%Y"))

        Result = Query()
        s1 = db.search(Result.dataId == rec["dataId"])

        if not s1:
            total_added += 1
            print ("Adding ... ", total_added)
            db.insert(rec)

    return soup

def clean_money(amt):
    return amt.replace(".","")

def clean_pic(ids):
    idlist = ids.split(",")
    first = idlist[0]
    code = first.replace("1:","")
    return "https://images.craigslist.org/%s_300x300.jpg" % code

def make_excel(db):
    Headlines = ["Data id", "Name", "Brand","Final price", "Price regular", "Saleoff", "Rate", "Numb review", "Delivery","Webpage", "Create date"]
    width_column = [10, 50, 20, 20, 20, 7, 7, 15, 22, 15, 30]
    row = 0
    workbook = xlsxwriter.Workbook('example.xlsx', {'strings_to_numbers':True})
    worksheet = workbook.add_worksheet('Data')
    money_format = workbook.add_format({'num_format':'###,###,###'})

    for i in range(10):
        worksheet.set_column(i, i, width_column[i])

    for col, title in enumerate(Headlines):
        worksheet.write(row, col, title)

    for item in db.all():
        row += 1
        worksheet.write(row, 0, item['dataId'])
        worksheet.write(row, 1, item['name'] )
        worksheet.write(row, 2, item['brand'])
        worksheet.write(row, 3, item['final-price'], money_format)
        worksheet.write(row, 4, item['price-regular'], money_format)
        worksheet.write(row, 5, item['saleoff'])
        worksheet.write(row, 6, item['rate'])
        worksheet.write(row, 7, item['review'])
        worksheet.write(row, 8, item['delivery'])
        worksheet.write_url(row, 9, item['webpage'], string='Web Page')
        worksheet.write(row, 10, item['createdt'])

    workbook.close()
def make_csv(db):
    print(db)
main(url)