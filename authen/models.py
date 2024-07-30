from django.db import models
import uuid
from django.contrib.auth.models import User
from PIL import Image
from django.conf import settings
import random
import string




class PinCode(models.Model):
	pin=models.CharField(max_length=100)

	def __str__(self):
		return self.pin

class Secrets(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return f"Secret for {self.user.username}"

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	avatar = models.ImageField(default=settings.DEFAULT_AVATAR, upload_to='profile_images')
	bio = models.TextField()

	def __str__(self):
	    return self.user.username

	# resizing images
	def save(self, *args, **kwargs):
	    super().save()

	    img = Image.open(self.avatar.path)

	    if img.height > 100 or img.width > 100:
	        new_img = (100, 100)
	        img.thumbnail(new_img)
	        img.save(self.avatar.path)
