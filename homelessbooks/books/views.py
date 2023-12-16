import json
import os
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Book, BookImage

def index(request):
    return render(request, "books/index.html")

def add_book(request):
        # Get categories
        categories = sorted(set(Book.objects.values_list("category", flat=True)))
        return render(request, "books/addbook.html", {
             "categories": categories
        })
   
def save_book(request):
     # Check it's post
     if request.method == "POST":
          
          # Get book data from form
          bookid = request.POST["book-id"]
          isbn_10 = request.POST["book-isbn-10"]
          isbn_13 = request.POST["book-isbn-13"]
          title = request.POST["book-title"]
          language = request.POST["book-language"]
          subtitle = request.POST["book-subtitles"]
          authors = request.POST["book-authors"]
          publisher = request.POST["book-publisher"]

          # Check how category was sent
          category = request.POST.get("book-category", None)

          published_date = request.POST["book-publication-date"]
          page_count = request.POST["book-page-count"]
          height = request.POST["book-height"]
          width = request.POST["book-width"]
          thickness = request.POST["book-thickness"]
          print_type = request.POST["book-print-type"]
          dust_jacket = request.POST.get("book-dust-jacket", None)
          description = request.POST["book-description"]
          binding = request.POST.get("book-binding", None)
          condition = request.POST.get("book-condition", None)

          # Extract images
          image_keys = [key for key in request.FILES.keys() if key.startswith("image_")]

          # Loop over and save images
          for key in image_keys:
               image = request.FILES[key]
               book_image = BookImage(image=image, bookid=bookid)
               book_image.save()

          # Create data dict to pass
          data = {
               "bookid": bookid,
               "isbn_10": isbn_10,
               "isbn_13": isbn_13,
               "title": title,
               "language" : language,
               "subtitle": subtitle,
               "authors": authors,
               "publisher": publisher,
               "category": category, 
               "published_date": published_date,
               "page_count": page_count, 
               "height": height,
               "width": width, 
               "thickness": thickness,
               "print_type": print_type,
               "dust_jacket": dust_jacket, 
               "description": description,
               "binding": binding,
               "condition": condition, 
          }
          
          # Make new book and save
          book = Book(**data)
          book.save()

          # Get associated images
          images = BookImage.objects.filter(bookid=bookid)

          # Get the just added book
          book = Book.objects.get(bookid=bookid)
          book.images.set(images)
          book.save()

          # Get id 
          id = book.id
          
          # Loop through images to connect book
          for image in images:
              image.book = book
              image.save()

          return JsonResponse({"message": "Book saved successfully", "id": id})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def delete_book(request, id):
     if request.method == "POST":
          # Get book
          book = Book.objects.get(id=id)

          # Delete book
          book.delete()

          return JsonResponse({"message": "Book saved deleted", "id": id})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def edit_book(request, id):
     if request.method == "GET":
          # Get book
          book = Book.objects.get(id=id)

          return render(request, "books/editbook.html" , {
               "book": book
          })

def book(request, id):
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

def get_api_key(request):
    google_api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    return JsonResponse({"google_api_key": google_api_key})

def inventory(request):
    # Get all books and categories
    books = Book.objects.all()
    categories = sorted(set(Book.objects.values_list("category", flat=True)))
    conditions = sorted(set(Book.objects.values_list("condition", flat=True)))


    return render(request,"books/inventory.html", {
         "books": books,
         "categories": categories,
         "conditions": conditions
    } )
