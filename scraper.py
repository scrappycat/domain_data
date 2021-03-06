# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import scraperwiki
from lxml import html, etree
from datetime import datetime
import csv
import urllib
import urllib2

# Purge the data
# try:
#	scraperwiki.sqlite.execute('DELETE FROM DATA')
# except:
#	print "Data not found yet. Continuing..."

extractedOn = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


def parse_page(state="vic", area="inner-east", region="melbourne-region", suburb="carnegie", postcode="3162", page=1):
    # Read in a page
    url_root = "http://www.domain.com.au/search/buy/state/%s/area/%s/region/%s/suburb/%s/?" % \
               (state, area, region, suburb)

    # /?ssubs=1&searchterm=caulfield%2c+vic%2c+3162&page=1
    page_address = url_root + urllib.urlencode(
            {"ssubs": "1", "searchterm": "%s,%s,%s" % (suburb, state, postcode), "page": page})

    # print page_address

    page_redirected_address = urllib2.urlopen(page_address).geturl()

    print "Scraping " + page_redirected_address

    html_string = scraperwiki.scrape(page_redirected_address)

    # Find something on the page using css selectors
    root = html.fromstring(html_string)
    for elem in root.xpath('//div[@class="listing-result__listing "]'):
        # print "---"
        # print etree.tostring(elem)
        # print "---"

        item = {
            "link": "",
            "address": "",
            "locality": "",
            "price": "",
            "beds": "",
        }

        link_elem = elem.xpath('.//a[@class="listing-result__listing"]/@href')
        if len(link_elem) > 0:
            item["link"] = "http://domain.com.au%s" % link_elem[0]

        address_elem = elem.xpath('.//span[@itemprop="streetAddress"]/text()')
        if len(address_elem) > 0:
            item["address"] = address_elem[0]

        locality_elem = elem.xpath('.//span[@itemprop="addressLocality"]/text()')
        if len(locality_elem) > 0:
            item["locality"] = locality_elem[0]

        price_elem = elem.xpath('.//h2[@class="listing-result__price"]/text()')
        if len(price_elem) > 0:
            item["price"] = "".join(price_elem[0].split("\\n")).strip()

        beds_elem = elem.xpath('.//span[@class="listing-result__feature-bed"]/text()')
        if len(beds_elem) > 0:
            item["beds"] = beds_elem[0].strip()

        # print item

        # Write out to the sqlite database using scraperwiki library
        scraperwiki.sqlite.save(unique_keys=['address', 'suburb'],
                                data={
                                    "link": item["link"],
                                    "address": item["address"],
                                    "suburb": item["locality"],
                                    "price": item["price"],
                                    "beds": item["beds"],
                                    "extracted_on": extractedOn,
                                })


dictReader = csv.DictReader(open('suburbs.csv', 'rb'))

for line in dictReader:
    for page_no in range(1, int(line["pages"])):
        parse_page(
                state=line["state"],
                area=line["area"],
                region=line["region"],
                suburb=line["suburb"],
                postcode=line["postcode"],
                page=page_no)
