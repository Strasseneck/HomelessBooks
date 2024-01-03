import requests 
from bs4 import BeautifulSoup

def scrape_booklooker(bookInfo):
        # Base search url
        base_url = "https://www.booklooker.de/B%C3%BCcher/Angebote/autor={AUTHOR}&verlag={PUBLISHER}&titel={TITLE}"
        
        # Extract info for plugging into url
        author = str(bookInfo["author"]).replace(' ', '+')
        publisher = str(bookInfo["publisher"]).replace(' ', '+')
        title = str(bookInfo["title"]).replace(' ', '+')

        # Create url for query by pluggin in values
        complete_url = base_url.format(AUTHOR=author, PUBLISHER=publisher, TITLE=title)
        print(complete_url)

        # Headers
        headers = {
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"  
        }

        # Make request
        response = requests.get(complete_url, headers=headers)
 
        if response.status_code == 200:
                # Get the html and parse
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Check for the more info link
                first_span = soup.find("span", id=lambda x: x and x.startswith("moreInfo_"))

                if first_span:
                        # Extract the link
                        more_info_url = first_span.find("a")["href"]

                        # Get the more info page
                        response = requests.get("https://www.booklooker.de" + more_info_url)

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
                                
                                # Create result dictionary
                                results = {
                                        "binding": binding,
                                        "condition": condition,
                                        "price": price,
                                        "seller": seller_name,
                                }

                                # Return results
                                return results








                                
                                
                





                





