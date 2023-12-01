// Get book info function

// Get button click
$('#isbn-submit').on('click', function () {
    console.log("isbn search clicked");
    let isbn = $('#isbn-search').val();
    getBookId(isbn);
})

// Get google volume id via ISBN
async function getBookDataIsbn(isbn) {
    console.log("function called");
    console.log(`ISBN: ${isbn}`);

    try {
        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`);
    
        if(!response.ok) {
            throw new Error(`HTTP error! Status ${response.status}`)
        }

        const result = await response.json();
        return result;
        }
        catch(error) {
            console.error("Error getting book data:", error);
            return null;
        }
}

// Get bookID function
async function getBookId(isbn) {
    let bookId;
    const result = await getBookDataIsbn(isbn);

    if(result !== null) {
        bookId = result.items[0].id;
    }
    else {
        console.log("Search returned no book data")
    }
}

