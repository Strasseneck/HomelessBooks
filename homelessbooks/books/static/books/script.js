// Get api key via fetch function
let googleApiKey;
let deeplApiKey;

// Get api keys if it's add_book page
function getApiKeys() {
    console.log('function get api keys');
    fetch('/get_api_keys')
        .then(response => {
            if(!response.ok) {
                throw new Error('Error retrieving API key');
            }
            return response.json();
        })
        .then(data => {
            const gApiKey = data.google_api_key;
            const dApiKey = data.deepl_api_key;
            // Assign to global variables
            googleApiKey = gApiKey;
            deeplApiKey = dApiKey;    
        })
        .catch(error => {
            console.error(error);
            return null;
        })
}

// Call get api keys function when the add_book page is loaded
document.addEventListener('DOMContentLoaded', function () {
    if(window.location.pathname === '/add_book') {
        getApiKeys();
        generateRandomUid();
    }  
})

// ISBN search button
$('#isbn-submit').on('click', function () {
    console.log('ISBN search clicked');
    // Define isbn variable and remove hyphens
    isbn = $('#isbn-search').val().replace(/-/g, '');
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
    const title = $('#title-search').val();
    const author = $('#author-search').val();
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
    // Call async function to get data
    const result = await getBookDataTitleAuthor(title, author);

    if(result !== null && result.items[0].id !== undefined) {
        // Get year
        let year = $('#published-search').val();
        let results = result.items;
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
    // Call async function to get data
    const result = await getBookDataIsbn(isbn);

    if(result !== null && result.items[0].id !== undefined) {
        // If valid book data returned get book id call function
        return getBookData(result.items[0].id);
    }
    else {
        console.log('Search returned no bookId')
    }
}

// Get book data with bookId function
function getBookData(bookId) {
    console.log('get book data with bookid function')
    console.log(bookId);
    // Get book volume resource using book id
    fetch(`https://www.googleapis.com/books/v1/volumes/${bookId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((json) => {
            displayBookData(json);
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
    $('#book-title').val(bookInfo.title);
    
    // check for possible isbns
    if(bookInfo.industryIdentifiers) {
       $('#book-isbn-10').val(bookInfo.industryIdentifiers[0].identifier);
       $('#book-isbn-13').val(bookInfo.industryIdentifiers[1].identifier);
    }
     
    $('#book-language').val(bookInfo.language)
    $('#book-subtitles').val(bookInfo.subtitle);
    $('#book-authors').val(bookInfo.authors);
    $('#book-publisher').val(bookInfo.publisher);

    // Check for category
    if(bookInfo.mainCategory) {
        addCategory(bookInfo.mainCategory);
    }
    else if(bookInfo.categories) {
       const category = (bookInfo.categories[0]).split('/')[0];
       addCategory(category);
    }
   
    $('#book-publication-date').val(bookInfo.publishedDate);
    $('#book-page-count').val(bookInfo.printedPageCount);
    

    // Check if dimensions included
    if(bookInfo.dimensions) {
        $('#book-height').val(bookInfo.dimensions.height);
        $('#book-width').val(bookInfo.dimensions.width);
        $('#book-thickness').val(bookInfo.dimensions.thickness);
    }
    $('#book-print-type').val(bookInfo.printType);

    // Check for html tags in description
    if(bookInfo.description) {
    const descriptionText = bookInfo.description.match(/<[^>]*>/g, '')
        ? bookInfo.description.replace(/<[^>]*>/g, '')
        : bookInfo.description;
    $('#book-description').val(descriptionText);
    }

    // Check for image src
    if(bookInfo.imageLinks) {
        // Call function to create image preview
        createImagePreview(bookInfo.imageLinks.smallThumbnail);
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

// Create image preview
$('#image-upload-button').on('click', function () {
    // Create preview
    const $input = $('#image-upload')[0];
    console.log($input);
    const file = $input.files;
    let image;
    if(file) {
        const fileReader = new FileReader();
        fileReader.onload = event => {
            image = event.target.result;
            createImagePreview(image);
        }
        fileReader.readAsDataURL(file[0]);
    }
    saveImage($input);
})

// Save image function
async function saveImage(input) {
    // Get token
    const token = $('[name="csrfmiddlewaretoken"]').val();
    const bookId = $('#bookid-image-upload').val();
    // Create form data
    const formData = new FormData();
    formData.append('image', input.files[0]);
    formData.append('bookId', bookId);

    // Make Fetch request
    fetch('/upload_image', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': token,
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    .catch(error => {
        console.error('Error:', error);
    })
}

// Generate random book id for linking images and book
function generateRandomUid() {
    $('#book-uid').val(Math.random().toString(36).substring(2,9));
    $('#bookid-image-upload').val($('#book-uid').val());
}

// Add category button
$('#add-category-button').on('click', addCategory);

// Add category function
function addCategory(returnedCategory) {
    console.log('Add category function clicked')
    
    // Remove dropdown
    $('#category-dropdown').remove();

    // Check for category
    const category = returnedCategory !== undefined ? returnedCategory : '';

    // Create input and insert
    $('<input>')
        .addClass('form-control form-control-sm')
        .attr('type', 'text')
        .attr('id', 'new-category-input')
        .val(category)
        .prependTo('#book-category');

    // Add new onlick listener
    $('#add-category-button')
        .off('click', addCategory)
}