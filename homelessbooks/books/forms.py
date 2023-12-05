from django import forms
from .models import BookImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = BookImage
        fields = ['image']

        widget = { 
            'image': forms.Select(attrs={'class': 'form-control form-control-sm'})
        }