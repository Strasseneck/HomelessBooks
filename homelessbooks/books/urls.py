from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_book", views.add_book, name="add_book"),
    path("save_book", views.save_book, name="save_book"),
    path("upload_image", views.upload_image, name="upload_image"),
    path("get_api_keys", views.get_api_keys, name="get_api_keys"),
    path("inventory", views.inventory, name="inventory")
]