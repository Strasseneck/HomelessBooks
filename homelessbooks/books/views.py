import json
import os
from abebooks import AbeBooks, AbeResult
from booklooker import BookLooker, BookLookerResult
from html import unescape
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import User
from books.models import Author, Book, BookImage

def index(request):
    if request.user.is_authenticated: 
         # get user info
         user = request.user

         # Books listed by user
         books_listed = Book.objects.filter(created_by=user)
         books_listed_count = books_listed.count()
         last_book_listed = books_listed.order_by("-created_at").first()
         books_without_images = books_listed.filter(images__isnull=True).count()

         print(last_book_listed)

         # Get data for dashboard
         books_count = Book.objects.all().count()

         # Get oldest and newest listing
         oldest_listings = Book.objects.all().order_by("created_at")
         if oldest_listings:
              oldest_listing = oldest_listings.first()
              newest_listing = oldest_listings.last()
          
              # Get images
              oldest_images = list(oldest_listing.images.values_list('image', flat=True))
              if oldest_images:
                    oldest_image = oldest_images.pop(0)
              else:
                   oldest_image = None

              newest_images = list(newest_listing.images.values_list('image', flat=True))
              if newest_images:
                    newest_image = newest_images.pop(0)
              else:
                   newest_image = None

         return render(request, "books/index.html", {
              "books_count": books_count,
              "oldest_listing": oldest_listing,
              "oldest_image": oldest_image,
              "newest_listing": newest_listing,
              "newest_image": newest_image,
              "user": user,
              "books_listed_count": books_listed_count,
              "last_book_listed": last_book_listed, 
              "books_without_images": books_without_images
         })
    else:
          return render(request, "books/login.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        print(username, password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Successful authentication
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            # Invalid login details
            return render(request, 'books/login.html', {'error_message': 'Invalid username or password'})

    else:
         return render(request, "books/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required    
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

@login_required  
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

               # Add edited by
               book.edited_by = request.user
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
               # Add created by
               book.created_by = request.user
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

@login_required
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

@login_required
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

@login_required
def get_abebooks_price(request):
     
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
               
               # Use abebooks class to get prices
               ab = AbeBooks()
               results_isbn = ab.getPriceByISBN(isbn)
               results_at = ab.getPriceByAuthorTitle(author, title)

               if results_isbn["success"] or results_at["success"]:
                    # Dict to return
                    abeResult = {
                         "results_isbn" : results_isbn,
                         "results_at": results_at
                    }

                    # Store in session
                    request.session["abeResult"] = abeResult

                    # Return message and result
                    return JsonResponse({"message": "success", "result": abeResult})
               else: 
                    # If no results return message
                    return JsonResponse({"message": "failure"})
               
          except json.JSONDecodeError:
               return HttpResponseBadRequest("Invalid JSON format")
          
          except Book.DoesNotExist:
               return JsonResponse({"message": "Book not found"})  
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

@login_required
def get_booklooker_price(request):   
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

               # Extract author, publisher, title
               author = list(book.authors.all())[0].name
               publisher = book.publisher
               title = book.title
               
               # Use booklooker class to get prices
               bl = BookLooker()
               results_isbn = bl.getPriceDataByISBN(isbn)
               results_apt = bl.getPriceDataByAuthorPublisherTitle(author, publisher, title)


               if results_isbn is not None or results_apt is not None:
                    booklookerResult = {}
                    if results_isbn:
                         booklookerResult["results_isbn"] = results_isbn
                    
                    if results_apt:
                        booklookerResult["results_apt"] = results_apt
                    
                    # Store in session
                    request.session["booklookerResult"] = booklookerResult

                    # Return message and result
                    return JsonResponse({"message": "success", "result": booklookerResult})
               else:
                    # If no results return message
                    return JsonResponse({"message": "failure"})

          except json.JSONDecodeError:
               return HttpResponseBadRequest("Invalid JSON format")
          
          except Book.DoesNotExist:
               return JsonResponse({"message": "Book not found"})  
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

@login_required
def display_pricecheck_results(request):
     # Creat dicts
     Abebooks_results = {}
     Booklooker_results = {}

     # Check for data in session
     abe_result = request.session.get("abeResult")
     bl_result = request.session.get("booklookerResult")

     if abe_result is not None:
          # Extract best used price
          best_used_abe_isbn = abe_result.get("results_isbn")["pricingInfoForBestUsed"]
          best_used_abe_at = abe_result.get("results_at")["pricingInfoForBestUsed"]
          
          if best_used_abe_isbn is not None:
               # If exists assign to dict
               abe_result_isbn = AbeResult(best_used_abe_isbn)
               Abebooks_results["isbn"] = abe_result_isbn
         
          if best_used_abe_at is not None:
               # If exists assign to dict
               abe_result_at = AbeResult(best_used_abe_at)
               Abebooks_results["at"] = abe_result_at

     if bl_result is not None:
           # Extract bl result
           best_result_isbn = bl_result.get("results_isbn") 
           best_result_apt = bl_result.get("results_apt")

           if best_result_isbn is not None:
               # If exists assign to dict 
               bl_result_isbn = BookLookerResult(best_result_isbn)   
               Booklooker_results["isbn"] =  bl_result_isbn
               
           if best_result_apt is not None: 
               # If exists assign to dict 
               bl_result_apt = BookLookerResult(best_result_apt)
               Booklooker_results["apt"] = bl_result_apt

     # Create dict for template
     pricecheck_results = {}      

     if Abebooks_results or Booklooker_results:         
          if Abebooks_results:
               pricecheck_results["Abebooks_results"] = Abebooks_results
          
          if Booklooker_results:
               pricecheck_results["Booklooker_results"] = Booklooker_results

          # Get book via stored id
          id = request.session.get("bookId")
          book = Book.objects.get(id=id)

          # Get images
          images = list(book.images.values_list('image', flat=True))
          first_image = images.pop(0)

          # Clear out session data
          request.session.clear()

          print(pricecheck_results)

          # Render template, passing data as context
          return render(request, "books/displaypriceresults.html", {
               "book": book,
               "pricecheck_results": pricecheck_results,
               "first_image": first_image,
               "images": images
          })
     
     else:
          # Get book via stored id
          id = request.session.get("bookId")
          book = Book.objects.get(id=id)

          # Get images
          images = list(book.images.values_list('image', flat=True))
          first_image = images.pop(0)

          # Clear out session data
          request.session.clear()

          # Render page with message
          return render(request, "books/displaypriceresults.html", {
               "book": book,
               "message": "No pricing info for this book available, sorry",
               "first_image": first_image,
               "images": images
          })

@login_required    
def book(request, id):
     if request.method == "GET":
          # Get book object
          book = Book.objects.get(id=id)

          # Get images
          images = list(book.images.values_list('image', flat=True))
          if images:
               first_image = images.pop(0)
          else:
               first_image = None

          return render(request, "books/book.html", {
               "book": book,
               "first_image": first_image,
               "images": images
          })
     else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")

@login_required
def get_api_key(request):
    if request.method == "GET":
          google_api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
          return JsonResponse({"google_api_key": google_api_key})
    else:
          # For none get requests
          return HttpResponseBadRequest("Invalid request method")

@login_required
def inventory(request):
    if request.method == "GET":
          # Get all books and all fields from dropdowns
          books = Book.objects.all()
          categories = sorted(set(Book.objects.values_list("category", flat=True)))
          conditions = sorted(set(Book.objects.values_list("condition", flat=True)))
          publishers = sorted(set(Book.objects.values_list("publisher", flat=True)))
          authors = Author.objects.all().values_list("name", flat=True)
          return render(request,"books/inventory.html", {
               "authors": authors,
               "books": books,
               "categories": categories,
               "conditions": conditions,
               "publishers": publishers
          })
    else:
         # For none get requests
         return HttpResponseBadRequest("Invalid request method")

@login_required
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