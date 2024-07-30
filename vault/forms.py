from django import forms
from .models import Folder, File,ExtractKey,EnterKey,Editor

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



class EditorForm(forms.ModelForm):
    class Meta:
        model=Editor
        fields="__all__"


class FileUpdateForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if File.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A file with this name already exists.")
        return name

class FolderUpdateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name',  'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'ckeditor'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
         