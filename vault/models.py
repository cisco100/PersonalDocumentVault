from ckeditor.fields import RichTextField
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cryptography.fernet import Fernet
from django.conf import settings
import base64, os
import uuid
from django.dispatch import receiver
from dotenv import load_dotenv


load_dotenv()
ID_ENCRYPTION_KEY = str(os.getenv('ID_ENCRYPTION_KEY'))



class Folder(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=255,unique=True)
    description = RichTextField()
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    def get_ancestors(self):
        ancestors = []
        folder = self
        while folder.parent_folder:
            folder = folder.parent_folder
            ancestors.insert(0, folder)
        return ancestors










class Key(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.TextField()
    private_key = models.TextField()

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         private_key = rsa.generate_private_key(
    #             public_exponent=65537,
    #             key_size=2048
    #         )
    #         public_key = private_key.public_key()
    #         self.private_key = private_key.private_bytes(
    #             encoding=serialization.Encoding.PEM,
    #             format=serialization.PrivateFormat.PKCS8,
    #             encryption_algorithm=serialization.NoEncryption()
    #         ).decode('utf-8')
    #         self.public_key = public_key.public_bytes(
    #             encoding=serialization.Encoding.PEM,
    #             format=serialization.PublicFormat.SubjectPublicKeyInfo
    #         ).decode('utf-8')
    #     super().save(*args, **kwargs)









# models.py add size
class File(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=255,unique=True)
    file = models.FileField(upload_to='files/')
    encrypted_data = models.BinaryField()
    encrypted_fernet_key = models.BinaryField()
    file_extension = models.CharField(max_length=10)  # Add this line
    size=models.BigIntegerField(default=0)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    qrcode=models.ImageField(upload_to='keys/')
    icon=models.ImageField(upload_to='icons/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

    def get_share_url(self):
        fernet = Fernet(ID_ENCRYPTION_KEY)
        value = fernet.encrypt(str(self.pk).encode())
        value = base64.urlsafe_b64encode(value).decode()
        return reverse("share-file-id", kwargs={"id": (value)})


class Trash(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trash')
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True, related_name='trashed_file')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='trashed_folder')
    deleted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trash item {self.id} by {self.user}"
    



class ExtractKey(models.Model):
    steg=models.ImageField()

class EnterKey(models.Model):
    key=models.TextField()

