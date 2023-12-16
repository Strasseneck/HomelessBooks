from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_book", views.add_book, name="add_book"),
    path("save_book", views.save_book, name="save_book"),
    path("book/edit_book/<int:id>", views.edit_book, name="edit_book"),
    path("book/<int:id>", views.book, name="book"),
    path("get_images/<int:id>", views.get_images, name="get_images"),
    path("get_api_key", views.get_api_key, name="get_api_key"),
    path("inventory", views.inventory, name="inventory")
]