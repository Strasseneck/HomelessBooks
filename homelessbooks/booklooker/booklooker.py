import requests 
from bs4 import BeautifulSoup
import re

class BookLooker:

        def __get_first_book(self, payload):
                url = "https://www.booklooker.de/B%C3%BCcher/Angebote/"
                
                if payload["action"] == "getPriceDataByISBN":
                        isbn = payload["isbn"]
                        url = url + f"isbn={isbn}"
                
                elif payload["action"] == "getPriceDataByAuthorPublisherTitle":
                        author = str(payload["author"]).replace(' ', '+')
                        publisher = str(payload["publisher"]).replace(' ', '+')
                        title = str(payload["title"]).replace(' ', '+')
                        url = url + f"autor={author}&verlag={publisher}&titel={title}"
                
                else: 
                        raise ValueError("Invalid action value: {}".format(payload.action))
                        
                headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"  
                }

                response = requests.get(url, headers=headers)
                response.raise_for_status()

                if response.status_code == 200:
                        # Get the html and parse
                        soup = BeautifulSoup(response.content, "html.parser")
                        
                        # Check for the more info link
                        first_span = soup.find("span", id=lambda x: x and x.startswith("moreInfo_"))

                        if first_span:
                                # Extract the link
                                more_info_url = first_span.find("a")["href"]
                                # Return function with url passed
                                return self.get_book_info(more_info_url)
                        
        def getPriceDataByISBN(self, isbn):
            """
            Parameters
            ----------
            isbn (int) - a book's ISBN code
            """
            payload = {
                   'action': 'getPriceDataByISBN',
                   'isbn': isbn
                   }
            return self.__get_first_book(payload)
        
        def getPriceDataByAuthorPublisherTitle(self, author, publisher, title):
            """
            Parameters
            ----------
            author (str) - book title
            publisher (str) - book publisher
            title = (str) - book title
            """
            payload = {
                   'action': 'getPriceDataByAuthorPublisherTitle',
                   'author': author,
                   'publisher': publisher,
                   'title': title
                   }
            return self.__get_first_book(payload)

        def get_book_info(self, url):
                # Get the more info page
                response = requests.get("https://www.booklooker.de" + url)

                if response.status_code == 200:
                        # Declare variables
                        condition = None
                        binding = None

                        # Get the html and parse
                        soup = BeautifulSoup(response.content, "html.parser")

                        # Get price
                        price_span = soup.find("span", class_="priceValue")
                        price = price_span.text if price_span else None

                        # Find all elements contain property names and values
                        property_names = soup.find_all("div", class_="propertyName")
                        property_values = soup.find_all("div", class_="propertyValue")

                        # Extract text content
                        for name, value in zip(property_names, property_values):
                                name_text = name.get_text(strip=True)
                                value_text = value.get_text(strip=True)

                                # Check for condition
                                if name_text == "Zustand:":
                                        condition = value_text

                                elif name_text == "Einband:":
                                        binding = value_text

                        # Check for seller name and location
                        div = soup.find("div", class_="sellerName")
                        seller_name = div.find("span", class_="notranslate")

                        seller_name = seller_name.text if seller_name else None
                        
                        message = "success" if price else "failure"

                        # Create result dictionary
                        results = {
                                "message": message,
                                "binding": binding,
                                "condition": condition,
                                "price": price,
                                "seller": seller_name,
                        }

                        # Return results
                        return results

class BookLookerResult:
    def __init__(self, data):
        self.platform = "Booklooker"
        self.binding = data.get("binding", "")
        self.condition = data.get("condition", "")
        self.currency = self.get_currency_symbol(data)
        self.price = self.strip_currency_symbol(data)
        self.seller = data.get("seller", "")

    def get_currency_symbol(self, data):
        price = data.get("price", "")
        currency_symbols = re.findall(r'[$€£¥₹]', price)
        if currency_symbols:
               return currency_symbols[0]
        return ""
    
    def strip_currency_symbol(self, data):
           price = data.get("price", "")
           return re.sub(r'[$€£¥₹]', "", price).strip()
