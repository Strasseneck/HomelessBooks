// ADD BOOK PAGE 
document.addEventListener('DOMContentLoaded', function () {
    if(window.location.pathname === '/add_book') {
        // GLOBAL VARIABLES

        // Book images array 
        const bookImages = [];

        // Get api key via fetch function
        let googleApiKey = getApiKey();

        // EVENT LISTENERS

        // ISBN search button event listener
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

        // Title author search button event listener
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

        // Upload image button event listener
        $('#image-upload-button').on('click', uploadImage);

        // Add category button
        $('#add-category-button').on('click', addCategory);

        // FUNCTIONS

        // Get api keys function
        function getApiKey() {
            fetch('/get_api_key')
                .then(response => {
                    if(!response.ok) {
                        throw new Error('Error retrieving API key');
                    }
                    return response.json();
                })
                .then(data => {
                    googleApiKey = data.google_api_key;   
                })
                .catch(error => {
                    console.error(error);
                    return null;
                })
        }

        // Add category function
        function addCategory(returnedCategory) {
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

            // Remove listener
            $('#add-category-button')
                .off('click', addCategory)
        }
        
        // SEARCH FUNCTIONS

        // Get google volume id via ISBN
        async function getBookDataIsbn(isbn) {
            console.log(googleApiKey);
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
                console.log(result);
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
                createImageThumbnail(bookInfo.imageLinks.thumbnail);
            }
        }

        // HANDLE IMAGE UPLOADS

        // Upload image function
        function uploadImage() {
            // Get image
            const $input = $('#image-upload')[0];
            const file = $input.files;
            if(file) {
                const fileReader = new FileReader();
                const fileName = file[0].name;
                fileReader.onload = event => {
                    const image = event.target.result;
                    // Create thumbnail
                    createImageThumbnail(image, fileName);
                }
                fileReader.readAsDataURL(file[0]);
                // Store image for database
                bookImages.push(file[0]);
                }
        }

        // Create thumbnail
        function createImageThumbnail(image, fileName) {
            // Create thumbnail container
            const $thumbnailContainer = $('<div>')
            $thumbnailContainer.addClass('thumbnail-container')
            $thumbnailContainer.prependTo('#image-previews'); 
            
            // Create thumbnail 
            const $thumbnail = $('<img>')
            $thumbnail.addClass('img-thumbnail')
            $thumbnail.attr('src', `${image}`)
            $thumbnail.on({ 
                mouseenter: function() {
                console.log("mouse over");

                // Check if button already exists
                if($thumbnailContainer.find('.thumbnail-close').length !== 0) {
                    return;
                }
                // Create button
                const $button = $('<button>')
                $button.addClass('btn-close thumbnail-close')
                // add remove image functionality 
                $button.on('click', function() {
                    // Delete image function
                    deleteImage(fileName);
                    $thumbnailContainer.remove();
                })
                // Append to the thumbnail container
                $thumbnailContainer.prepend($button); 
            }        
            })
            // Add button to container
            .appendTo($thumbnailContainer)

            // Remove button when mouse leaves previews
            const $imagePreviews = $('#image-previews').on({
                mouseleave: function() {
                    // Remove button on mouseleave
                    $imagePreviews.find('.thumbnail-close').remove()
                }
            })
        }

        // Save image function
        function saveImage(input) {
            // Get token
            const token = $('[name="csrfmiddlewaretoken"]').val();
            // Create form data
            const formData = new FormData();
            formData.append('images', bookImages);
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

        // Delete image function
        function deleteImage(fileName) {
            const toDelete = bookImages.find((element) => element.name === fileName);
            const indexToRemove = bookImages.indexOf(toDelete);
            bookImages.splice(indexToRemove, 1)  
        }
    }
})