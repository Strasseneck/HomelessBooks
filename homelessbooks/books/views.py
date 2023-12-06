import json
import os
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm

def index(request):
    return render(request, "books/index.html")

def add_book(request):
    # Check for POST
    if request.method == "POST":
        # Create form populate with data
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save image
            form.save()
    # If any other method, blank form
    else:
        form = ImageUploadForm()
        return render(request, "books/addbook.html", {'form': form})

def get_api_keys(request):
    google_api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    deepl_api_key = os.environ.get("DEEPL_API_KEY")
    return JsonResponse({'google_api_key': google_api_key, 'deepl_api_key': deepl_api_key})

def inventory(request):
    return 
