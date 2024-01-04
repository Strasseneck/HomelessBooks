import requests
from currency_symbols import CurrencySymbols

class AbeBooks:

    def __get_price(self, payload):
        url = "https://www.abebooks.de/servlet/DWRestService/pricingservice"
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return resp.json()


    def getPriceByISBN(self, isbn):
        """
        Parameters
        ----------
        isbn (int) - a book's ISBN code
        """
        payload = {'action': 'getPricingDataByISBN',
                   'isbn': isbn,
                   'container': 'pricingService-{}'.format(isbn)}
        return self.__get_price(payload)

    def getPriceByAuthorTitle(self, author, title):
        """
        Parameters
        ----------
        author (str) - book author
        title (str) - book title
        """
        payload = {'action': 'getPricingDataForAuthorTitleStandardAddToBasket',
                   'an': author,
                   'tn': title,
                   'container': 'oe-search-all'}
        return self.__get_price(payload)

class AbeResult:
    def __init__(self, data):
        self.platform = "Abebooks"
        self.location = data.get("vendorCountryNameInSurferLanguage", "")
        self.condition = data.get("bookCondition", "")
        self.currency = self.get_currency_symbol(data)
        self.price = data.get("bestPriceInPurchaseCurrencyValueOnly", "")
        self.postage = data.get("bestShippingToDestinationPriceInPurchaseCurrencyValueOnly", "")
        self.total = self.calculate_total(data)

    def get_currency_symbol(self, data):
        cs = CurrencySymbols()
        currency = data.get("purchaseCurrencySymbol")
        currency = currency.strip("()',")
        return cs.get_symbol(currency)


    def calculate_total(self, data):
        total_price = float(data.get("bestPriceInPurchaseCurrencyValueOnly", "0"))
        shipping_price = float(data.get("bestShippingToDestinationPriceInPurchaseCurrencyValueOnly", "0"))
        total = total_price + shipping_price
        return "{:.2f}".format(total)
