from django import forms
from vault.models import Folder,File

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = "__all__"



class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = "__all__"



