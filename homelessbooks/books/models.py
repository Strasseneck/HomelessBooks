from django.db import models
from django.core.validators import MinValueValidator

class Book(models.Model):
    title = models.CharField(max_length=750)
    subtitle = models.CharField(max_length=750)
    authors = models.CharField(max_length=750)
    publisher = models.CharField(max_length=750)
    category = models.CharField(max_length=100)
    published_date = models.CharField(max_length=8)
    page_count = models.IntegerField(validators=[MinValueValidator(1)])
    height = models.DecimalField(max_digits=5, decimal_places=2)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    thickness = models.DecimalField(max_digits=5, decimal_places=2)
    print_type = models.CharField(max_length=10)
    dust_jacket = models.CharField(max_length=10)
    description = models.TextField()
    binding = models.CharField(max_length=10)
    condition = models.CharField(max_length=10)
    images = models.ManyToManyField('BookImage', blank=True, related_name='photos')

class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book_images/')



