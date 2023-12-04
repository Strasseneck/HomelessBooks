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

def index(request):
    return render(request, "books/index.html")

def add_book(request):
    return render(request, "books/addbook.html")

def get_api_key(request):
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    return JsonResponse({'api_key': api_key})

def inventory(request):
    return 
