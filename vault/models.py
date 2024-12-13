from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
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
    description = RichTextField(config_name='editor')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_ancestors(self):
        ancestors = []
        folder = self
        while folder.parent_folder:
            folder = folder.parent_folder
            ancestors.insert(0, folder)
        return ancestors






class Editor(models.Model):
    content=RichTextUploadingField(config_name='editor_config')



class Key(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.TextField()
    private_key = models.TextField()

 





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
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.name



    def get_share_url(self):
        return reverse("share-file", kwargs={"file_id": str(self.id)})

 
class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('upload', 'Upload'),
        ('download', 'Download'),
        ('share', 'Share'),
        ('delete-file', 'Delete-File'),
        ('update-File', 'Update-File'),
        ('delete-folder', 'Delete-Folder'),
        ('update-folder', 'Update-Folder'),
        ('restore-folder', 'Restore-Folder'),
        ('restore-file', 'Restore-File'),
        ('trash-file', 'Trash-File'),
        ('trash-folder', 'Trash-Folder'),
        ('trash-delete-file', 'Trash-Delete-File'),
        ('trash-delete-folder', 'Trash-Delete-Folder'),

        ('create-folder', 'Create-Folder'),
    ) 
  
    #fix logging by adding name of item to which the activiy i s coming from,on the display let it be just a card-link when clicked will open the log page and the content can be exported to pdf
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"






 




class Trash(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trash')
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True, related_name='trashed_file')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='trashed_folder')
    trashed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trash item {self.id} by {self.user}"
    



class ExtractKey(models.Model):
    steg=models.ImageField()

class EnterKey(models.Model):
    key=models.TextField()

