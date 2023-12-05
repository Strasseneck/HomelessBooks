// Get api key via fetch function
let googleApiKey;

function getApiKey() {
    console.log('function get api key');
    fetch('/get_api_key')
        .then(response => {
            if(!response.ok) {
                throw new Error('Error retrieving API key');
            }
            return response.json();
        })
        .then(data => {
            let apiKey = data.api_key;
            console.log(apiKey);
            // assign to global variable
            googleApiKey = apiKey;
        })
        .catch(error => {
            console.error(error);
            return null;
        })
}

document.addEventListener('DOMContentLoaded', function () {
    getApiKey();
})

// ISBN search button
$('#isbn-submit').on('click', function () {
    console.log('ISBN search clicked');
    // Define isbn variable
    let isbn = $('#isbn-search').val();
    // Remove hypens
    isbn = isbn.replace(/-/g, '');
    console.log(isbn)
    if(isbn !== '') {
        // Call get book id function
        getBookIdIsbn(isbn);
    }
    else {
        console.log('no ISBN input');
        return;
    }
    
})

// Title author search button
$('#title-author-submit').on('click', function () {
    console.log('title author search clicked');
    // define title and author
    let title = $('#title-search').val();
    let author = $('#author-search').val();
    if(title !== "" && author !== "") {
        getBookIdTitleAuthor(title, author);
    }
    else {
        console.log('Title or author missing');
        return;
    }
})

// Get google volume id via ISBN
async function getBookDataIsbn(isbn) {
    console.log('isbn search function called');
    console.log(`ISBN: ${isbn}`);

    try {
        // Request book data using isbn
        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}&key=${googleApiKey}`);
    
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

// Get book data title and author
async function getBookDataTitleAuthor(title, author) {
    console.log('Title author search function called');
    console.log(`Title: ${title}`);
    console.log(`Author: ${author}`);
    try {
        // Request book data using isbn
        const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${title}+inauthor:${author}&key=${googleApiKey}`);
    
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

// Get google volume id via title and author
async function getBookIdTitleAuthor(title, author) {
    let bookId;
    // Call async function to get data
    const result = await getBookDataTitleAuthor(title, author);

    if(result !== null && result.items[0].id !== undefined) {
        // Get year
        let year = $('#published-search').val();
        let results = result.items;
        console.log(results);
        // Loop through results to find published in year
        const book = results.find(result => result.volumeInfo.publishedDate.includes(year));
        if(book) {
            return getBookData(book.id);
        }
    }
    else {
        console.log('Search returned no bookId')
    }

}

// Get bookId with ISBN function
async function getBookIdIsbn(isbn) {
    let bookId;
    // Call async function to get data
    const result = await getBookDataIsbn(isbn);

    if(result !== null && result.items[0].id !== undefined) {
        // If valid book data returned get book id call function
        bookId = result.items[0].id;
        return getBookData(bookId);
    }
    else {
        console.log('Search returned no bookId')
    }
}

// Get book data with bookId function
function getBookData(bookId) {
    console.log('get book data with bookid function')
    console.log(bookId);
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
    console.log(bookInfo);

    // Get form elements and display info
    const $title = $('#book-title').val(bookInfo.title);
    const $subtitles = $('#book-subtitles').val(bookInfo.subtitle);
    const $authors = $('#book-authors').val(bookInfo.authors);
    const $publisher = $('#book-publisher').val(bookInfo.publisher);
    const $category = $('#book-category')
    const $publicationDate = $('#book-publication-date').val(bookInfo.publishedDate);
    const $pageCount = $('#book-page-count').val(bookInfo.printedPageCount);

    // Check if dimensions included
    if(bookInfo.dimensions) {
        const $height = $('#book-height').val(bookInfo.dimensions.height);
        const $width = $('#book-width').val(bookInfo.dimensions.width);
        const $thickness = $('#book-thickness').val(bookInfo.dimensions.thickness);
    }
    const $printType = $('#book-print-type').val(bookInfo.printType);
    const $description = $('#book-description');

    // Generate book description
    const bookLanguage = bookInfo.language;

    let descriptionText = stripHtmlTags(bookInfo.description);
    $description.val(descriptionText);

    // Check for image src
    if(bookInfo.imageLinks.smallThumbnail !== undefined) {
        console.log("There is an image associated")
        let image = bookInfo.imageLinks.smallThumbnail;
        // Call function to create image preview
        createImagePreview(image);
    }
}
// Preview image
function createImagePreview(image) {
    // create element and append to images container
    $('<img>')
    .addClass('img-thumbnail')
    .attr('src', `${image}`)
    .appendTo('#image-previews');
}

// Strip html tags
function stripHtmlTags(text) {
    return text.replace(/<[^>]*>/g, '');
}