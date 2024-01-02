// Global Variables

// Current path
const currentPath = window.location.pathname;

// Book array
const bookImages = [];

// Images to delete array
const deleteImages = [];

// Global Functions

// Upload image function
function uploadImage() {
  // Get image
  const $input = $("#image-upload")[0];
  const file = $input.files;
  if (file) {
    const fileReader = new FileReader();
    const fileName = file[0].name;
    fileReader.onload = (event) => {
      const image = event.target.result;
      // Create thumbnail
      createImageThumbnail(image, null, fileName);
    };
    fileReader.readAsDataURL(file[0]);
    // Store image for database
    bookImages.push(file[0]);
  }
}

// Create thumbnail
function createImageThumbnail(image, id = null, fileName = null) {
  // Create thumbnail container
  const $thumbnailContainer = $("<div>");
  $thumbnailContainer.addClass("thumbnail-container");
  $thumbnailContainer.prependTo("#image-previews");

  // Create thumbnail
  const $thumbnail = $("<img>");
  $thumbnail.addClass("img-thumbnail");
  $thumbnail.attr("src", `${image}`);
  $thumbnail
    .on({
      mouseenter: function () {
        // Check if button already exists
        if ($thumbnailContainer.find(".thumbnail-close").length !== 0) {
          return;
        }
        // Create button
        const $button = $("<button>");
        $button.addClass("btn-close thumbnail-close");
        // add remove image functionality
        $button.on("click", function () {
          // Delete image function
          if (fileName !== null) {
            deleteImage(fileName);
          }
          if (id !== null) {
            deleteImages.push(id);
          }
          $thumbnailContainer.remove();
        });
        // Append to the thumbnail container
        $thumbnailContainer.prepend($button);
      },
    })
    // Add button to container
    .appendTo($thumbnailContainer);

  // Remove button when mouse leaves previews
  const $imagePreviews = $("#image-previews").on({
    mouseleave: function () {
      // Remove button on mouseleave
      $imagePreviews.find(".thumbnail-close").remove();
    },
  });
}

// Delete image function
function deleteImage(fileName) {
  const toDelete = bookImages.find((element) => element.name === fileName);
  const indexToRemove = bookImages.indexOf(toDelete);
  bookImages.splice(indexToRemove, 1);
}

// Save book function
function saveBook() {
  // Get token
  const token = $('[name="csrfmiddlewaretoken"]').val();

  // Check if it's new or edit book

  if ($("#new-book-form").length > 0) {
    // It's a new book

    // Create form data
    const newBookForm = $("#new-book-form")[0];
    const formData = new FormData(newBookForm);
    const bookTitle = $("#book-title").val();

    // Loop to append each image
    bookImages.forEach((bookImage, index) => {
      formData.append(`image_${bookTitle}_${index}`, bookImage);
    });

    // Make Fetch request
    fetch("/save_book", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const id = data.id;
        // Redirect to book
        window.location.href = `/book/${id}`;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    // It's an update of an existing book
    // Create form data
    const editBookForm = $("#edit-book-form")[0];
    const formData = new FormData(editBookForm);
    const bookTitle = $("#book-title").val();

    // Check for images to delete
    if (deleteImages.length !== 0) {
      // Loop to append each image
      deleteImages.forEach((deleteImage, index) => {
        formData.append(`delete_id_${index}`, deleteImage);
      });
    }

    // Check for new image uploads
    if (typeof bookImages !== "undefined") {
      // Loop to append each image
      bookImages.forEach((bookImage, index) => {
        formData.append(`image_${bookTitle}_${index}`, bookImage);
      });
    }

    // Make Fetch request
    fetch("/save_book", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const id = data.id;
        // Load book saved
        window.location.href = `/book/${id}`;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
}

// Get images for book
async function getImages(id) {
  try {
    const response = await fetch(`/get_images/${id}`);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    // Convert to array
    const returnedImages = data.images;

    return returnedImages;
  } catch (error) {
    console.error("Error:", error);
    // Rethrow the error or handle it as needed
    throw error;
  }
}

// PAGE SPECIFIC FUNCTIONS
document.addEventListener("DOMContentLoaded", function () {
  // ADD BOOK PAGE
  if (currentPath.startsWith("/add_book")) {
    // Variables

    const bookImages = [];
    // Generate random uid for books and images
    generateRandomUid();

    // Get api key via fetch function
    let googleApiKey = getApiKey();

    // Event listeners

    // ISBN search button event listener
    $("#isbn-submit").on("click", function () {
      // Define isbn variable and remove hyphens
      isbn = $("#isbn-search").val().replace(/-/g, "");
      if (isbn !== "") {
        // Call get book id function
        getBookIdIsbn(isbn);
      } else {
        $("#isbn-search").attr(
          "placeholder",
          "Please enter a valid ISBN number!"
        );
      }
    });

    // Title author search button event listener
    $("#title-author-publisher-submit").on("click", function () {
      // define title and author
      const title = $("#title-search").val();
      const author = $("#author-search").val();
      const publisher = $("#publisher-search").val();
      if (title !== "" && author !== "" && publisher !== "") {
        getBookIdTitleAuthorPublisher(title, author, publisher);
      } else {
        $("#title-search").attr("placeholder", "Please enter a title...");
        $("#author-search").attr("placeholder", "and author...");
        $("#publisher-search").attr("placeholder", "...and publisher!");
      }
    });

    // Upload image button event listener
    $("#image-upload-button").on("click", uploadImage);

    // Add category button
    $("#add-category-button").on("click", addCategory);

    // Save book and images on click Event listener
    $("#save-book-button").on("click", saveBook);

    // Functions

    // Get api keys function
    function getApiKey() {
      fetch("/get_api_key")
        .then((response) => {
          if (!response.ok) {
            throw new Error("Error retrieving API key");
          }
          return response.json();
        })
        .then((data) => {
          googleApiKey = data.google_api_key;
        })
        .catch((error) => {
          console.error(error);
          return null;
        });
    }

    // Generate random book id for linking images and book
    function generateRandomUid() {
      $("#book-id").val(Math.random().toString(36).substring(2, 9));
    }

    // Add category function
    function addCategory() {
      // Remove dropdown
      $("#category-dropdown").remove();

      // Create input and insert
      $("<input>")
        .addClass("form-control form-control-sm")
        .attr("type", "text")
        .attr("id", "new-category-input")
        .attr("name", "book-category")
        .prependTo("#book-category");

      // Remove listener
      $("#add-category-button").off("click", addCategory);
    }

    // SEARCH FUNCTIONS

    // Get google volume id via ISBN
    async function getBookDataIsbn(isbn) {
      try {
        // Request book data using isbn
        const response = await fetch(
          `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}&key=${googleApiKey}`
        );

        if (!response.ok) {
          throw new Error(`HTTP error! Status ${response.status}`);
        }

        // If response is okay store result and return
        const result = await response.json();
        console.log(result);
        return result;
      } catch (error) {
        // Catch errors
        console.error("Error getting book data:", error);
        return null;
      }
    }

    // Get book data title and author
    async function getBookDataTitleAuthorPublisher(title, author, publisher) {
      try {
        // Request book data using isbn
        const response = await fetch(
          `https://www.googleapis.com/books/v1/volumes?q=${title}+inauthor:${author}+inpublisher:${publisher}&key=${googleApiKey}`
        );

        if (!response.ok) {
          throw new Error(`HTTP error! Status ${response.status}`);
        }

        // If response is okay store result and return
        const result = await response.json();
        return result;
      } catch (error) {
        // Catch errors
        console.error("Error getting book data:", error);
        return null;
      }
    }

    // Get google volume id via title and author
    async function getBookIdTitleAuthorPublisher(title, author, publisher) {
      // Call async function to get data
      const result = await getBookDataTitleAuthorPublisher(
        title,
        author,
        publisher
      );

      if (result !== null && result.items[0].id !== undefined) {
        // Get year
        let year = $("#year-search").val();
        let results = result.items;
        // Loop through results to find published in year
        const book = results.find((result) =>
          result.volumeInfo.publishedDate.includes(year)
        );
        if (book) {
          return getBookData(book.id);
        }
      } else {
        console.log("Search returned no bookId");
      }
    }

    // Get bookId with ISBN function
    async function getBookIdIsbn(isbn) {
      // Call async function to get data
      const result = await getBookDataIsbn(isbn);

      if (result !== null && result.items[0].id !== undefined) {
        // If valid book data returned get book id call function
        return getBookData(result.items[0].id);
      } else {
        console.log("Search returned no bookId");
      }
    }

    // Get book data with bookId function
    function getBookData(bookId) {
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
          console.error("Error:", error);
        });
    }

    // Display returned book data in form
    function displayBookData(bookData) {
      const bookInfo = bookData.volumeInfo;

      // Get form elements and display info
      $("#book-title").val(bookInfo.title);

      // check for possible isbns
      if (bookInfo.industryIdentifiers) {
        $("#book-isbn-10").val(bookInfo.industryIdentifiers[0].identifier);
        $("#book-isbn-13").val(bookInfo.industryIdentifiers[1].identifier);
      }

      $("#book-language").val(bookInfo.language);
      $("#book-subtitles").val(bookInfo.subtitle);
      $("#book-authors").val(bookInfo.authors);
      $("#book-publisher").val(bookInfo.publisher);

      // Check for category
      if (bookInfo.mainCategory) {
        addCategory(bookInfo.mainCategory);
      } else if (bookInfo.categories) {
        const category = bookInfo.categories[0].split("/")[0].trim();
        $("#choose-category").remove();
        $("<option>")
          .val(category)
          .text(category)
          .attr("selected", "")
          .prependTo("#category-dropdown");
      }

      $("#book-publication-date").val(bookInfo.publishedDate);
      $("#book-page-count").val(bookInfo.printedPageCount);

      // Check if dimensions included
      if (bookInfo.dimensions) {
        $("#book-height").val(bookInfo.dimensions.height);
        $("#book-width").val(bookInfo.dimensions.width);
        $("#book-thickness").val(bookInfo.dimensions.thickness);
      }
      $("#book-print-type").val(bookInfo.printType);

      // Check for html tags in description
      if (bookInfo.description) {
        const descriptionText = bookInfo.description.match(/<[^>]*>/g, "")
          ? bookInfo.description.replace(/<[^>]*>/g, "")
          : bookInfo.description;
        $("#book-description").val(descriptionText);
      }

      // Check for image src
      if (bookInfo.imageLinks) {
        // Call function to create image preview
        createImageThumbnail(bookInfo.imageLinks.thumbnail);
      }
    }
  }
  // BOOK PAGE
  else if (currentPath.startsWith("/book")) {
    //Event listeners

    // Price Comparison
    $("#price-comparison-button").on("click", function () {
      const bookId = this.dataset.bookId;
      priceComparison(bookId);
    });

    // Delete book button
    $("#delete-book-button").on("click", function () {
      const id = $(this).val();
      deleteBook(id);
    });

    // Functions

    // Price comparison
    async function priceComparison(id) {
      // Get token
      const token = $('[name="csrfmiddlewaretoken"]').val();

      try {
        // Send request via fetch
        const response = await fetch("/get_abebooks_price", {
            method: "POST",
            body: id,
            headers: { "X-CSRFToken": token},
          });
      
        const data = await response.json();
        console.log(data);
        if (data.message === "Success") {
          window.location.href = "display_pricecheck_results"
        }
        } 
        catch (error) {
          console.error("Error", error);
        }
    }

    // Delete book function
    function deleteBook(id) {
      // Get token
      const token = $('[name="csrfmiddlewaretoken"]').val();

      // Make Fetch request
      fetch("/delete_book", {
        method: "POST",
        body: id,
        headers: {
          "X-CSRFToken": token,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          window.location.href = "/inventory";
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }
  // EDIT BOOK PAGE
  else if (currentPath.startsWith("/edit_book")) {
    // Variables

    // Book images array
    const bookImages = [];

    // Images to delete array
    const deleteImages = [];

    // Event listeners

    // Add category button
    $("#add-category-button").on("click", addCategory);

    // Save book and images on click Event listener
    $("#save-book-button").on("click", saveBook);

    // Upload image button event listener
    $("#image-upload-button").on("click", uploadImage);

    const id = $("#id").val();
    // Get images
    getImages(id)
      .then((response) => {
        // Loop to create thumbnails
        response.forEach((image) =>
          createImageThumbnail(image.path, image.id, null)
        );
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
  // INVENTORY PAGE
  else if (currentPath.startsWith("/inventory")) {
    // Variables
    let returnedInventory = [];
    let conditionsChecked = [];
    let toDelete = [];

    // Event listeners

    // Search bar
    $("#inventory-search").on("input", function () {
      const query = $(this).val().toLowerCase();
      searchInventory(query);
    });

    // Condition sort dropdown
    $(".condition-checkbox").on("change", function () {
      // Check if the value is currently clicked
      const checkbox = $(this).val();
      if (this.checked) {
        // Box selected
        conditionCheckboxSelected(checkbox);
      } else {
        // Box deselected
        conditionCheckboxDeselected(checkbox);
      }
    });

    // Multi delete button
    $("#multiple-delete-button").on("click", addChecksDelete)

    // Select all checkbox
    $("#select-all-checkbox").on("change", function () {
      if (this.checked) {
        // Add all to delete array
        const rows = Array.from($(".inventory-row"));
        rows.forEach((row) => {
          const bookId = row.dataset.bookId;
          toDelete.push(bookId);
        })
      }
      else {
        // Remove all from delete array
        toDelete = [];
      }
    })

    // Individual checkboxes
    $(".inventory-checkbox").on("change", function () {
      const bookId = this.dataset.bookId;
      console.log(`checked ${bookId}`)
      if (this.checked) {
        // Add to delete array
        toDelete.push(bookId);
      }
      // if it's been unchecked
      else {
        toDelete.indexOf(bookId);
        toDelete.splice(index, 1);
      }
    })

    // Functions

    // Condition checkbox clicked
    function conditionCheckboxSelected(checkbox) {
      // Add to array call sorting function
      conditionsChecked.push(checkbox);
      sortByCondition(conditionsChecked);
    }

    // Condition checkbox unclicked
    function conditionCheckboxDeselected(checkbox) {
      // Remove from array call sorting function
      const index = conditionsChecked.indexOf(checkbox);
      conditionsChecked.splice(index, 1);
      sortByCondition(conditionsChecked);
    }

    // Sort by condition
    function sortByCondition(conditionsChecked) {
      // Clear out array
      returnedInventory = [];
      const rows = Array.from($(".inventory-row"));
      if (conditionsChecked.length !== 0) {
        // Return all matching rows
        rows.forEach((row) => {
          const condition = `${row.cells[5].innerText.toLowerCase()}`;
          if (conditionsChecked.includes(condition)) {
            returnedInventory.push(row);
          }
        });
      } else {
        // Return all rows
        rows.forEach((row) => {
          returnedInventory.push(row);
        });
      }
      displayResult(returnedInventory);
    }

    // Search inventory
    function searchInventory(query) {
      // Clear out array
      returnedInventory = [];
      // Get current rows
      const inventoryRows = $(".inventory-row").toArray();
      inventoryRows.forEach((row) => {
        // Make array of cells per row
        const cells = Array.from(row.cells);
        // Check if search query is in cells
        const containsQuery = cells.some((cell) =>
          cell.textContent.toLowerCase().includes(query)
        );
        if (containsQuery) {
          // if it contains search add to array
          returnedInventory.push(row);
        }
      });
      // Display / hide inventory rows
      return displayResult(returnedInventory);
    }

    // Add selects and delete
    function addChecksDelete() {
      // Make checkboxes visible
      $("#inventory-checkbox-header").attr("hidden", false);
      $(".checkbox-row").attr("hidden", false);
      // Change Multiple button to delete button, remove event listener, add new event listener
      $("#multiple-delete-button")
        .attr("id", "delete-button")
        .text("Delete")
        .off("click")
        .on("click", function () {
          deleteBooks(toDelete);
        })
    }

    // Delete books
    function deleteBooks(toDelete) {
      // Remove event listener
      $("#delete-button").off("click");

      // Get token
      const token = $('[name="csrfmiddlewaretoken"]').val();

      // Convert array to list
      const body = JSON.stringify(toDelete);

      // Make Fetch request
      fetch("/delete_book", {
        method: "POST",
        body: body,
        headers: {
          "X-CSRFToken": token,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          window.location.href = "/inventory";
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }

    // Display result function
    function displayResult(inventory) {
      // Get currently showing rows
      const currentRows = Array.from($(".inventory-row"));
      currentRows.forEach((row) => {
        if (!inventory.includes(row)) {
          // Hide row
          const $toHide = $(`#${row.id}`);
          $toHide.attr("hidden", true);
        } else {
          // Show row
          const $toShow = $(`#${row.id}`);
          $toShow.attr("hidden", false);
        }
      });
    }
  }
});
