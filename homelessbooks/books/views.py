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
        categories = list(Book.objects.values_list("category", flat=True))
        return render(request, "books/addbook.html", {
             "categories": categories
        })

def save_book(request):
     # Check it's post
     if request.method == "POST":
          
          # Get book data from form
          bookid = request.POST["book-id"]
          title = request.POST["book-title"]
          subtitle = request.POST["book-subtitles"]
          authors = request.POST["book-authors"]
          publisher = request.POST["book-publisher"]
          category = request.POST["book-category"]
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

          # Get associated images
          images = BookImage.objects.filter(bookid=bookid)

          # Create data dict to pass
          data = {
               "title": title,
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
          
          # Save book
          book = Book(**data)
          book.save()
          book.images.set(images)
          book.save()
          return JsonResponse({"message" : "Book saved successfully"})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")


def upload_image(request):
     # Check it's post
     if request.method == "POST":
          # Get image and save it
          image = request.FILES["image"]
          bookid = request.POST.get("bookId")
          book_image = BookImage(image=image, bookid=bookid)
          book_image.save() 
          # Return response if succesful
          return JsonResponse({"message" : "Image saved successfully"})
     else:
          # For none post requests
          return HttpResponseBadRequest("Invalid request method")

def get_api_keys(request):
    google_api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    deepl_api_key = os.environ.get("DEEPL_API_KEY")
    return JsonResponse({"google_api_key": google_api_key, "deepl_api_key": deepl_api_key})

def inventory(request):
    return 
