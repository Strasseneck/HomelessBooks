from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_view", views.login_view, name="login"),
    path("logout_view", views.logout_view, name="logout_view"),
    path("add_book", views.add_book, name="add_book"),
    path("save_book", views.save_book, name="save_book"),
    path("delete_book", views.delete_book, name="delete_book"),
    path("edit_book/<int:id>", views.edit_book, name="edit_book"),
    path("book/<int:id>", views.book, name="book"),
    path("get_images/<int:id>", views.get_images, name="get_images"),
    path("get_abebooks_price", views.get_abebooks_price, name="get_abebooks_price"),
    path("get_booklooker_price", views.get_booklooker_price, name="get_booklooker_price"),
    path("book/display_pricecheck_results", views.display_pricecheck_results, name="display_pricecheck_results"),
    path("get_api_key", views.get_api_key, name="get_api_key"),
    path("inventory", views.inventory, name="inventory")
]