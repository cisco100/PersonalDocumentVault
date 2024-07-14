from django.contrib import admin
from vault.models import File,Folder,Key,Trash
# Register your models here.

admin.site.register(File)
admin.site.register(Folder)
admin.site.register(Key)
admin.site.register(Trash)