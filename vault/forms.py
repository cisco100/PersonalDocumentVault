from django import forms
from .models import Folder, File,ExtractKey,EnterKey

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('name','description')

class FileUploadForm(forms.ModelForm):
    file = forms.FileField()  # Add this field to handle file uploads

    class Meta:
        model = File
        fields = ['name', 'file']


class ExtractKeyForm(forms.ModelForm):
    class Meta:
        model=ExtractKey
        fields="__all__"


class EnterKeyForm(forms.ModelForm):
    class Meta:
        model=EnterKey
        fields="__all__"