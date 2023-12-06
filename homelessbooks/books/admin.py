from django.contrib import admin
from .models import Book, BookImage

class imageAdmin(admin.ModelAdmin):
    list_display = ["book", "image"]

# Register your models here.
admin.site.register(Book)
admin.site.register(BookImage)
