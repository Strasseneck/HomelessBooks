# HomelessBooks

This project is both my capstone project for CS50W Web Development with Javascript and Python and an application with real utility for a friend's book-selling business. It's primary goal is to streamline book listing and pricing and efficiently manage the inventory.

## Technology Stack

- **Backend:** Developed using Django, providing a robust foundation, makes use of Python's requests library and Beautiful Soup for webscraping.
- **Frontend:** Utilizes JavaScript, jQuery, and Bootstrap for a user-friendly interface.

## Key Features

- Integration with Google Books API for automated book information retrieval and form population.
- Automated generation of book listing details based on user input and the data returned by Google Books API.
- I've utilized the [Abebooks Rest API](https://github.com/ravila4/abebooks) to retrieve Abebooks price info and wrap it in a custom Class for rendering.
- Custom web scraping module leveraging Beautiful Soup to scrape Booklooker for pricing and book information.
- Dynamic and easy to understand user interface for sorting and interacting with the seller's inventory of books.
- Custom dark theme and look based on the client's preferences.
- Responsive thanks to Boostrap and Flexbox

## Distinctiveness and Complexity

This project is distinct from other projects in the course despite being in essence, a part of a larger e-commerce web application (it will eventually be used in combination with a Shopify shop), due to it's use of the Google Books API to retrieve book information and the use of the Abebooks REST API and Beautiful Soup to scrape for prices.

Incorporating these APIs required the use of asynchronous requests on the client side, increasing the complexity of the javascript code as well as requiring the use of custom python classes and modules on the server side. It also involved a more thorough understanding of how network requests and the HTML methods work, as well as navigating the API's documentation.

As well as that my project has a distinctly more complex dashboard and inventory view than any other project on the course. The add book view allows for upload and saving of images that are rendered as both thumbnails and stored as full sized images. The inventory search bar and selections allow for a dynamic searching experience, that required some complex DOM manipulation. 

Another element that adds to the complexity of the project is the way that it takes the data returned by the Google Books API and uses that in combination with the users own input and selection to dynamically generate the book's listing in the database, automating the step of writing a description before listing it on any book selling site.

## Images and Video Demo




