from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from .forms import SignupForm, PhotoForm
from .models import Album, Photo
from django.contrib.auth.models import User
from django.views.generic import DeleteView, ListView, DetailView, CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.
class LandingPageView(TemplateView):
    template_name = 'gallerize/landing.html'

class Login(LoginView):
    template_name = 'login_page/login.html'
    redirect_authenticated_user = True

class Logout(LogoutView):
    next_page = reverse_lazy('landing')

class Signup(CreateView):
    form_class = SignupForm
    template_name = 'login_page/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        email = self.request.POST.get('email')
        if email:
            user.email = email
        user.save()
        return redirect('login')
    
class HomeView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Album
    template_name = 'gallerize/home.html'
    context_object_name = 'albums'

    def get_queryset(self):
        # 🛠️ Admins see the latest 5 albums across the entire platform
        if self.request.user.is_superuser:
            return Album.objects.all().order_by('-id')[:5]
        return Album.objects.filter(artist=self.request.user).order_by('-id')[:5]
    
    def test_func(self):
        return self.request.user.is_authenticated
    

class AlbumListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Album
    template_name = 'gallerize/album_list.html'
    context_object_name = 'albums'
    ordering = ['-id']

    def test_func(self):
        return self.request.user.is_authenticated
    
    def get_queryset(self):
        # 🛠️ Admins see all albums globally
        if self.request.user.is_superuser:
            return Album.objects.all().order_by('-id')
        return Album.objects.filter(artist=self.request.user).order_by('-id')
    

class AlbumDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Album
    template_name = 'gallerize/album_photos_view.html'
    context_object_name = 'album'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_queryset(self):
        # 🛠️ Allow prefetching across all records if superuser
        if self.request.user.is_superuser:
            return Album.objects.all().prefetch_related('photos')
        return Album.objects.filter(artist=self.request.user).prefetch_related('photos')

    def get_object(self, queryset=None):
        album = super().get_object(queryset)
        # 🛠️ Bypass checking matching artist IDs if the user is an admin
        if not self.request.user.is_superuser and album.artist != self.request.user:
            raise PermissionDenied("You do not have permission to view this album.")
        return album
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        return context
    
class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    template_name = 'gallerize/create_album.html'
    fields = ['title', 'release_date', 'cover_image'] 
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.artist = self.request.user
        return super().form_valid(form)
    

class AlbumDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # 🛠️ Admins can target any album; regular users only target theirs
        if request.user.is_superuser:
            album = get_object_or_404(Album, id=pk)
        else:
            album = get_object_or_404(Album, id=pk, artist=request.user)
        album.delete()
        return redirect('home')

    def post(self, request, pk):
        if request.user.is_superuser:
            album = get_object_or_404(Album, id=pk)
        else:
            album = get_object_or_404(Album, id=pk, artist=request.user)
        album.delete()
        return redirect('home')
    
class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Album
    template_name = 'gallerize/edit_album.html'
    fields = ['title', 'release_date', 'cover_image']

    def test_func(self):
        # 🛠️ Admins bypass the artist matching boundary rule
        if self.request.user.is_superuser:
            return True
        album = self.get_object()
        return self.request.user == album.artist    

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.pk})
    
class PhotoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Photo
    template_name = 'gallerize/photos_list.html' 
    context_object_name = 'photos'
    paginate_by = 12

    def test_func(self):
        return self.request.user.is_authenticated
    
    def get_queryset(self):
       
        if self.request.user.is_superuser:
            return Photo.objects.all().order_by('-id')
        
        else:
            return Photo.objects.filter(posted_by=self.request.user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                context['user_albums'] = Album.objects.all()
            else:
                context['user_albums'] = Album.objects.filter(artist=self.request.user)
        else:
            context['user_albums'] = Album.objects.none()
        return context
    
class PhotoAlbumUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # 🛠️ Admin lookup scope extension
        if request.user.is_superuser:
            photo = get_object_or_404(Photo, id=pk)
        else:
            photo = get_object_or_404(Photo, id=pk, posted_by=request.user)
            
        album_id = request.POST.get('album_id')
        
        if album_id:
            if request.user.is_superuser:
                album = get_object_or_404(Album, id=album_id)
            else:
                album = get_object_or_404(Album, id=album_id, artist=request.user)
            photo.album = album
        else:
            photo.album = None
            
        photo.save()
        return redirect('photos_list')
    

class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    form_class = PhotoForm 
    template_name = 'gallerize/add_photo.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
class PhotoDetailView(LoginRequiredMixin, DetailView):
    model = Photo
    template_name = 'gallerize/photo_detail.html'
    context_object_name = 'photo'

class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo
    context_object_name = 'photo'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        photo = super().get_object(queryset)
        if not self.request.user.is_superuser and photo.posted_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this photo.")
        return photo

class Add_Photo_to_Album(LoginRequiredMixin, CreateView, UserPassesTestMixin):
    model = Photo
    template_name = 'gallerize/add_photo.html'
    fields = ['album', 'image', 'caption']
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        # 🛠️ Admins can instantly append to any context collection ID
        if self.request.user.is_superuser:
            return True
        album_id = self.kwargs.get('album_id')
        album = get_object_or_404(Album, id=album_id)
        return self.request.user == album.artist