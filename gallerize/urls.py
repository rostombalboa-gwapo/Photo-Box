from django.urls import path
from . import views


urlpatterns = [    
    path('', views.LandingPageView.as_view(), name='landing'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('album/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('album/create/', views.AlbumCreateView.as_view(), name='album_create'),
    path('albums/', views.AlbumListView.as_view(), name='album_list'),
    path('album/<int:pk>/update/', views.AlbumUpdateView.as_view(), name='album_update'),
    path('album/<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album_delete'), 
    path('photo/create/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('photos/', views.PhotoListView.as_view(), name='photos_list'),
    path('photo/<int:pk>/album/', views.PhotoAlbumUpdateView.as_view(), name='photo_album_update'), 
]