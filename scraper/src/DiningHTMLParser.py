import requests
import warnings
from lxml import html

# HTML parser for TripAdvisor Dining pages
class DiningHtmlParser:
    def __init__(self):
        self.attrs = {}
        self.__tree = None

    def parseUrl(self, url):
        page = requests.get(url)
        self.__tree = html.fromstring(page.text)
        # extract various attributes using xpath queries
        self.__parsePhoneNumber()
        self.__parseAddress()
        self.__parsePriceRange()
        self.__parseReviewStats()
        self.__parseName()
        self.__parseCuisine() # list
        self.__parseTime() # dict: day -> hours
        self.__parseCoordinates()
    
    def __parsePhoneNumber(self):
        phoneNumber = self.__tree.xpath('//div[@class="fl phoneNumber"]/text()')
        if phoneNumber:
            self.attrs['phoneNumber'] = phoneNumber[0]

    def __parseAddress(self):
        address = ''.join(filter(lambda x: x != '\n', self.__tree.xpath('//address//text()')))
        self.attrs['address'] = address

    # FIXME occasional failure to parse phone number for w/e reason. Need to dump tree to check and implement retry
    # TODO currently parsing CAD prices due to cookie; perhaps change to USD
    def __parsePriceRange(self):
        priceRange = self.__tree.xpath('//div[@class="detail"][contains(b, "Price range")]/span/text()')
        if priceRange:
            self.attrs['priceRange'] = priceRange[0].encode('ascii','ignore')
        else:
            warnings.warn('Cannot parse phone number')

    def __parseReviewStats(self):
        return

    def __parseName(self):
        dinerName = ''.join(map(lambda x: x.strip(), self.__tree.xpath('id("HEADING")/text()')))
        self.attrs['dinerName'] = dinerName

    def __parseCuisine(self):
        cuisines = map(lambda x: x.strip(), self.__tree.xpath('//span[@class="cuisine"]/text()'))
        if cuisines:
            self.attrs['cuisine'] = cuisines
        else:
            warnings.warn('Cannot parse cuisine type')

    def __parseTime(self):
        intervals = self.__tree.xpath('//div[span/@class="day" and span/@class="hours"]')
        openTime = {}
        for div in intervals:
            day = ''.join(map(lambda x: x.strip(), div.xpath('span[@class="day"]/text()')))
            hours = div.xpath('span[@class="hours"]/text()')
            openTime[day] = hours
        self.attrs['openTime'] = openTime

    def __parseCoordinates(self):
        mapDiv = self.__tree.xpath('//div[@class="mapContainer"]')
        if mapDiv:
            lat = mapDiv[0].xpath('@data-lat')
            lng = mapDiv[0].xpath('@data-lng')
            if lat and lng:
                self.attrs['latitude'] = lat[0]
                self.attrs['longitude'] = lng[0]

    def __str__(self):
        return '\n'.join(['{}:  \t{}'.format(k, v) for k,v in self.attrs.iteritems()])

def main():
    # tests the attraction html parser
    print("tests the dining page html parser")
    testUrl = "http://www.tripadvisor.ca/Restaurant_Review-g60763-d1743386-Reviews-Colicchio_Sons-New_York_City_New_York.html"
    parser = DiningHtmlParser()
    parser.parseUrl(testUrl)
    print(parser)

if __name__ == "__main__":
    main()
