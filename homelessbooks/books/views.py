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
        return render(request, "books/addbook.html")

def save_book(request):
     # Check it's post
     if request.method == "POST":
          
          # Get book data from form
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
          dust_jacket = request.POST["book-dust-jacket"]
          description = request.POST["book-description"]
          binding = request.POST["book-binding"]
          condition = request.POST["book-condition"]


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
