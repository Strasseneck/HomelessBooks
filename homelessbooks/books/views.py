import json
import os
from abebooks import AbeBooks, AbeResult
from html import unescape
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Author, Book, BookImage

def index(request):
    if request.method == "GET":
         return render(request, "books/index.html")
    else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")
         
def add_book(request):
        if request.method == "GET":       
             # Get categories
             categories = sorted(set(Book.objects.values_list("category", flat=True)))
             return render(request, "books/addbook.html", {
                    "categories": categories
             })
        else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")
   
def save_book(request):
     # Check it's post
     if request.method == "POST":
          # Extract authors and split if multiple
          authors = request.POST["book-authors"]
          authors = authors.split(",")

          # Get book data from form
          book_data = {
               "bookid": request.POST["book-id"],
               "isbn_10": request.POST["book-isbn-10"],
               "isbn_13": request.POST["book-isbn-13"],
               "title": request.POST["book-title"],
               "language": request.POST["book-language"],
               "subtitle": request.POST["book-subtitles"],
               "publisher": request.POST["book-publisher"],
               "category": request.POST.get("book-category", None),
               "published_date": request.POST["book-publication-date"],
               "page_count": request.POST["book-page-count"],
               "height": request.POST["book-height"],
               "width": request.POST["book-width"],
               "thickness": request.POST["book-thickness"],
               "print_type": request.POST["book-print-type"],
               "dust_jacket": request.POST.get("book-dust-jacket", None),
               "description": request.POST["book-description"],
               "binding": request.POST.get("book-binding", None),
               "condition": request.POST.get("book-condition", None),
          }

          # Extract id if present
          id = request.POST.get("id")
          if id is not None:          
               # Book instance already exists
               book = Book.objects.get(id=id)

               # Convert saved data to dict for comparison
               old_book_data = model_to_dict(book)

               # Remove authors for comparison
               if 'authors' in old_book_data:
                    del old_book_data['authors']

               if old_book_data != book_data:
                    # Update where necessary
                    for key, value in book_data.items():
                         setattr(book, key, value)

               book.save()
               
               # Check for new images
               image_keys = [key for key in request.FILES.keys() if key.startswith("image_")]

               # Loop over and save images
               for key in image_keys:
                    image = request.FILES[key]
                    book_image = BookImage(image=image, book=book)
                    book_image.save()
               
                # Get associated images
               images = BookImage.objects.filter(book=book)

               # Get the just added book
               book = Book.objects.get(id=book.id)
               book.images.set(images)
               book.save()

               # Check for images to delete
               for key in request.POST.keys():
                    if key.startswith('delete_'):
                         # Retrieve book image instance and delete
                         id = request.POST[key]
                         bookImage = BookImage.objects.get(id=id)
                         bookImage.delete()

               # Get id          
               id = book.id
               return JsonResponse({"message": "Book updated successfully", "id": id})
               
          else:
               # Make new book and save
               book = Book(**book_data)
               # Save book
               book.save()
               # Add authors
               book.authors.set([Author.objects.get_or_create(name=author.strip())[0] for author in authors])
               # Save again
               book.save()

               # Extract images
               image_keys = [key for key in request.FILES.keys() if key.startswith("image_")]

               # Loop over and save images
               for key in image_keys:
                    image = request.FILES[key]
                    book_image = BookImage(image=image, book=book)
                    book_image.save()

               # Get associated images
               images = BookImage.objects.filter(book=book)

               # Get the just added book
               book = Book.objects.get(id=book.id)
               book.images.set(images)
               book.save()

               id = book.id
               return JsonResponse({"message": "Book saved successfully", "id": id})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def delete_book(request):
     if request.method == "POST":
          try:
               # Extract content of body
               body = request.body.decode("utf-8")
               ids = json.loads(body)
               
               if isinstance(ids, list):
                    # List means multiple to delete
                    for id in ids:
                         # Get book
                         book = Book.objects.get(id=id)
                         # Delete book
                         book.delete()

                         deleted_ids = json.dumps(ids)
                         # Return json response
                         return JsonResponse({"message": "Books deleted", "ids": deleted_ids})

               elif isinstance(ids, str):
                    # String means single id
                    # Get book
                    book = Book.objects.get(id=ids)

                    # Delete book
                    book.delete()

                    # Return json response
                    return JsonResponse({"message": "Book deleted", "id": id})
               else:
                    # Invalid format
                    return HttpResponseBadRequest("Invalid IDs format")
               
          except json.JSONDecodeError:
               return HttpResponseBadRequest("Invalid JSON format")
          
          except Book.DoesNotExist:
               return JsonResponse({"message": "Book or books not found"})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def edit_book(request, id):
     if request.method == "GET":
          # Get book
          book = Book.objects.get(id=id)

          # Get categories
          categories = sorted(set(Book.objects.values_list("category", flat=True)))

          return render(request, "books/editbook.html" , {
               "book": book,
               "categories": categories
          })
     else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")

def get_abebooks_price(request):
     # Clear out session data
     request.session.clear()
     
     if request.method == "POST":
          try:
               # Extract book's id
               id = request.body.decode("utf-8")

               # Get book 
               book = Book.objects.get(id=id)
               request.session["bookId"] = book.id
     
               # Check for isbn_13
               if book.isbn_13:
                    # Extract isbn 13
                    isbn = int(book.isbn_13)

               # Check for isbn_10
               elif book.isbn_10:
                    # Extract isbn_10
                    isbn = int(book.isbn_10)

               # Extract author and shift first and last name 
               author_name = list(book.authors.all())[0].name
               author_names = author_name.split(" ")
               if len(author_names) > 1:
                    author = f"{author_names[-1]} {' '.join(author_names[:-1])}"
               else:
                    author = author_name

               title = book.title
               
               # Use abebooks module to get prices
               ab = AbeBooks()
               # With isbn
               results_isbn = ab.getPriceByISBN(isbn)
               results_at = ab.getPriceByAuthorTitle(author, title)
               if results_isbn["success"] or results_at["success"]:
                    # Store in session
                    request.session["abebooks_price_data_isbn"] = results_isbn 
                    request.session["abebooks_price_data_at"] = results_at
                    # Dict to return
                    result = {
                         "results_isbn" : results_isbn,
                         "results_at": results_at
                    }
                    # Return message and result
                    return JsonResponse({"message": "success", "result" : result})
               else: 
                    # If no results return message
                    return JsonResponse({"message": "Failure"})
               
          except json.JSONDecodeError:
               return HttpResponseBadRequest("Invalid JSON format")
          
          except Book.DoesNotExist:
               return JsonResponse({"message": "Book not found"})  
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def display_pricecheck_results(request):
     # Check for data in session
     results_isbn = request.session.get("abebooks_price_data_isbn")
     results_at = request.session.get("abebooks_price_data_at")

     # Extract best used price
     results_isbn = results_isbn["pricingInfoForBestUsed"]
     results_at = results_at["pricingInfoForBestUsed"]

     # Create dicts for display
     result_isbn = AbeResult(results_isbn)
     result_at = AbeResult(results_at)

     # Store in dict
     abe_results = {
          "isbn": result_isbn,
          "at": result_at,
     }

     # Check results exist
     if results_isbn or results_at:
          # Get book via stored id
          id = request.session.get("bookId")
          book = Book.objects.get(id=id)

          # Get images
          images = list(book.images.values_list('image', flat=True))
          first_image = images.pop(0)

          # Render template, passing data as context
          return render(request, "books/displaypriceresults.html", {
               "book": book,
               "abe_results": abe_results,
               "first_image": first_image,
               "images": images
          })

     else:
          # Reload original book page
          bookId = request.session.get("bookId")
          new_url = f"book/{bookId}"
          return HttpResponseRedirect(new_url)
     
def book(request, id):
     if request.method == "GET":
          # Get book object
          book = Book.objects.get(id=id)

          # Get images
          images = list(book.images.values_list('image', flat=True))
          first_image = images.pop(0)

          return render(request, "books/book.html", {
               "book": book,
               "first_image": first_image,
               "images": images
          })
     else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")

def get_api_key(request):
    if request.method == "GET":
          google_api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
          return JsonResponse({"google_api_key": google_api_key})
    else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")

def inventory(request):
    if request.method == "GET":
          # Get all books and categories
          books = Book.objects.all()
          categories = sorted(set(Book.objects.values_list("category", flat=True)))
          conditions = sorted(set(Book.objects.values_list("condition", flat=True)))
          return render(request,"books/inventory.html", {
               "books": books,
               "categories": categories,
               "conditions": conditions
          })
    else:
         # For none get requests
         return HttpResponseBadRequest("Invalid request method")

def get_images(request, id):
      if request.method == "GET":
          # Get book
          book = Book.objects.get(id=id)

          # Get associated images
          bookImages = BookImage.objects.filter(book=book)
          images = []
          for image in bookImages:
               data = {
                    'path': unescape(image.image.url),
                    'id': image.id
               }
               images.append(data)
          return JsonResponse({"images": images})
      else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")