from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_book", views.add_book, name="add_book"),
    path("get_api_keys", views.get_api_keys, name="get_api_keys"),
    path("inventory", views.inventory, name="inventory")
]