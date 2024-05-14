from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cryptography.fernet import Fernet
from django.conf import settings
import base64, os
from django.dispatch import receiver
from dotenv import load_dotenv

# Create your models here.
load_dotenv()

SECRET_KEY = bytes(str(os.getenv('SECRET_KEY')),'utf-8')

class Folder(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name=models.CharField(max_length=100)
	description=models.CharField(max_length=255)
	parent=models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name="subfolders")
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	class Meta:
		ordering = ('-created',)
	def __str__(self):
		return self.user.username + '-' + self.name

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    folder=models.ForeignKey(Folder,on_delete=models.CASCADE,related_name="files",null=True,blank=True)
    file_path = models.FileField(upload_to='uploads/files/',blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    encryption_status  =models.BooleanField()

    def __str__(self):
        return self.user.username + '-' + self.name

    def get_share_url(self):
        fernet = Fernet(settings.ID_ENCRYPTION_KEY)
        value = fernet.encrypt(str(self.pk).encode())
        value = base64.urlsafe_b64encode(value).decode()
        return reverse("share-file-id", kwargs={"id": (value)})

@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_path:
        if os.path.isfile(instance.file_path.path):
            os.remove(instance.file_path.path)

@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file_path
    except sender.DoesNotExist:
        return False

    new_file = instance.file_path
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)





























