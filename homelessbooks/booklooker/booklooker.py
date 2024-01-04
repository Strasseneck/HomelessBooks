import requests 
from bs4 import BeautifulSoup

class BookLooker:

        def __get_first_book(self, payload):
                url = "https://www.booklooker.de/B%C3%BCcher/Angebote/"
                
                if payload.action == "getPriceDataByISBN":
                        isbn = payload.isbn
                        url = url + f"={isbn}"
                
                elif payload.action == "getPriceDataByAuthorPublisherTitle":
                        author = payload.author
                        publisher = payload.publisher
                        title = payload.title
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

                                return self.__get_book_info(more_info_url)
                        
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
                   'author': author.replace(' ', '+'),
                   'publisher': publisher.replace(' ', '+'),
                   'title': title.replace(' ', '+')
                   }
            return self.__get_first_book(payload)



                





