from django.shortcuts import render, redirect
from vault.models import Folder, File
from vault.forms import FolderForm, FileForm

# Create your views here.

def cover_view(request):
	return render(request,"main/cover.html",{})

def folder_list(request):
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'folder_list.html', {'folders': folders})

def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            folder.save()
            return redirect('folder_list')
    else:
        form = FolderForm()
    return render(request, 'create_folder.html', {'form': form})

def upload_file(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user
            file.folder = folder
            file.save()
            return redirect('folder_detail', folder_id=folder_id)
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {'form': form, 'folder': folder})

def folder_detail(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    files = folder.files.all()
    return render(request, 'folder_detail.html', {'folder': folder, 'files': files})
