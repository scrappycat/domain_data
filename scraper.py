# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
from lxml import html
from datetime import datetime

extractedOn = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

# Read in a page
html_string = scraperwiki.scrape("http://www.domain.com.au/search/buy/state/vic/area/inner-east/region/melbourne-region/suburb/carnegie")

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

# Write out to the sqlite database using scraperwiki library
scraperwiki.sqlite.save(unique_keys=['address', 'extracted_on'],
                        data={
                            "link": item["link"],
                            "address": item["address"],
                            "price": item["price"],
                            "beds": item["beds"],
                            "extracted_on": extractedOn
                        })
