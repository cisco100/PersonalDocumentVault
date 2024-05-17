from django import forms
from vault.models import Folder, File

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name','file']