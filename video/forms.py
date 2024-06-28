# forms.py
from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video']
class SearchForm(forms.Form):
    query = forms.CharField(max_length=255)
    
