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
    images = models.ManyToManyField('BookImage', related_name='photos')

    def __str__(self):
        return self.title

class BookImage(models.Model):
    book = models.ForeignKey(Book, null=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book_images/')
    bookid = models.CharField(max_length=8, null=True)

    def __str__(self):
        return f"{self.book.title if self.book else 'No Book'} - Image{self.id}"



