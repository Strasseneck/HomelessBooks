from django.contrib import admin
from .models import Author, Book, BookImage

class imageAdmin(admin.ModelAdmin):
    list_display = ["book", "image"]

# Register your models here
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookImage)
