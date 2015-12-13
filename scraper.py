# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
from lxml import html
from datetime import datetime
import csv
import urllib

# Purge the data
try:
	scraperwiki.sqlite.execute('DELETE FROM DATA')
except:
	print "Data not found yet. Continuing..."

extractedOn = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

def parse_page(state="vic", area="inner-east", region="melbourne-region", suburb="carnegie", postcode="3162", page=1):
    # Read in a page
    url_root = "http://www.domain.com.au/search/buy/state/%s/area/%s/region/%s/suburb/%s/?" % \
        (state, area, region, suburb)

    #/?ssubs=1&searchterm=caulfield%2c+vic%2c+3162&page=1
    html_string = scraperwiki.scrape(url_root + urllib.urlencode({
        "ssubs": "1",
        "searchterm": "%s,%s,%s" % (suburb, state, postcode),
        "page": page
    }))

    # Find something on the page using css selectors
    root = html.fromstring(html_string)
    for elem in root.xpath('//a[@class="link-block"]'):

        item = {
            "link": "",
            "address": "",
            "price": "",
            "beds": "",
        }

        link_elem = elem.xpath("./@href")
        if len(link_elem)>0:
            item["link"] = "http://domain.com.au%s" % link_elem[0]

        address_elem = elem.xpath('.//h3[contains(@class,"address")=true()]/text()')
        if len(address_elem)>0:
            item["address"]=address_elem[0]

        price_elem = elem.xpath('.//h4[contains(@class,"pricepoint")=true()]/text()')
        if len(price_elem)>0:
            item["price"]=price_elem[0]

        beds_elem = elem.xpath('.//span[substring(text(),1,3)="Bed"]/../span/em/text()')
        if len(beds_elem)>0:
            item["beds"]=beds_elem[0].strip()

        # print item

        # Write out to the sqlite database using scraperwiki library
        scraperwiki.sqlite.save(unique_keys=['address'],
                                data={
                                    "link": item["link"],
                                    "address": item["address"],
                                    "price": item["price"],
                                    "beds": item["beds"],
                                    "extracted_on": extractedOn,
                                })


dictReader = csv.DictReader(open('suburbs.csv', 'rb'))

for line in dictReader:
    for page_no in range(1,int(line["pages"])):
        parse_page(
            state=line["state"],
            area=line["area"],
            region=line["region"],
            suburb=line["suburb"],
            postcode=line["postcode"],
            page=page_no)