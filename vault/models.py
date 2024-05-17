from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cryptography.fernet import Fernet
from django.conf import settings
import base64, os
from django.dispatch import receiver
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
User=get_user_model()


# Create your models here.
load_dotenv()

SECRET_KEY = bytes(str(os.getenv('SECRET_KEY')),'utf-8')


from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
# Watch the ancestors well, there is a bug
    def get_ancestors(self):
        ancestors = []
        folder = self
        while folder.parent_folder:
            folder = folder.parent_folder
            ancestors.insert(0, folder)
        return ancestors


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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





























