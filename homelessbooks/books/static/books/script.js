// Get book info function

// Get button click
$('#isbn-submit').on('click', function () {
    console.log('ISBN search clicked');
    // Define isbn variable
    let isbn = $('#isbn-search').val();
    // Remove hypens
    isbn = isbn.replace(/-/g, '');
    console.log(isbn)
    if(isbn !== '') {
        // Call get book id function
        getBookId(isbn);
    }
    else {
        console.log('no ISBN input');
        return;
    }
    
})

// Get google volume id via ISBN
async function getBookDataIsbn(isbn) {
    console.log('isbn search function called');
    console.log(`ISBN: ${isbn}`);

    try {
        // Request book data using isbn
        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`);
    
        if(!response.ok) {
            throw new Error(`HTTP error! Status ${response.status}`)
        }

        // If response is okay store result and return
        const result = await response.json();
        return result;
        }
        catch(error) {
            // Catch errors
            console.error('Error getting book data:', error);
            return null;
        }
}

// Get bookId function
async function getBookId(isbn) {
    let bookId;
    // Call async function to get data
    const result = await getBookDataIsbn(isbn);

    if(result !== null && result.items[0].id !== undefined) {
        // If valid book data returned get book id call function
        bookId = result.items[0].id;
        console.log(`Book Volume ID : ${bookId}`);
        getBookData(bookId);
    }
    else {
        console.log('Search returned no bookId')
    }
}

// Get book data with bookId function
function getBookData(bookId) {
    console.log('get book data with bookid function')
    let bookData;
    // Get book volume resource using book id
    fetch(`https://www.googleapis.com/books/v1/volumes/${bookId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((json) => {
            bookData = json;
            displayBookData(bookData);
        })
        .catch((error) => {
            // Handle error
            console.error('Error:', error);
        });  
}

// Display returned book data in form
function displayBookData(bookData) {
   
    const bookInfo = bookData.volumeInfo;

    // Get form elements and display info
    const $title = $('#book-title').val(bookInfo.title);
    const $subtitles = $('#book-subtitles').val(bookInfo.subtitle);
    const $authors = $('#book-authors').val(bookInfo.authors);
    const $publisher = $('#book-publisher').val(bookInfo.publisher);
    const $category = $('#book-category')
    const $publicationDate = $('#book-publication-date').val(bookInfo.publishedDate);
    const $pageCount = $('#book-page-count').val(bookInfo.printedPageCount);
    const $height = $('#book-height').val(bookInfo.dimensions.height);
    const $width = $('#book-width').val(bookInfo.dimensions.width);
    const $thickness = $('#book-thickness').val(bookInfo.dimensions.$thickness);
    const $printType = $('#book-print-type').val(bookInfo.printType);
    const $description = $('#book-description').val(bookInfo.description);
a


}
