# Generated by Django 4.2.7 on 2023-12-06 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_book_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='images',
            field=models.ManyToManyField(related_name='photos', to='books.bookimage'),
        ),
        migrations.AlterField(
            model_name='bookimage',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='books.book'),
        ),
    ]
