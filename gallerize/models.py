from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Album(models.Model):
    title = models.CharField(max_length=255,null=False,blank=False)
    artist = models.ForeignKey(User,on_delete=models.CASCADE,related_name='albums',null=True,blank=True)
    release_date = models.DateField(null=True,blank=True )
    cover_image = CloudinaryField('image',folder='album_covers/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.title} by {self.artist.username}"


class Photo(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos',null=True,blank=True)
    album = models.ForeignKey(Album,related_name='photos',on_delete=models.CASCADE,null=True,blank=True)
    image = CloudinaryField('image',folder='album_photos/',null=True,blank=True)
    caption = models.CharField(max_length=255,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
    def __str__(self):
        return f"Photo for {self.album.title}"