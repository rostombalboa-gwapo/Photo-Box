from django import forms
from .models import Album, Photo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm




class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'release_date', 'cover_image']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['album', 'image', 'caption']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_superuser:
                self.fields['album'].queryset = Album.objects.all().order_by('-id')
            else:
                self.fields['album'].queryset = Album.objects.filter(artist=user).order_by('-id')
