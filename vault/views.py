from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Folder,File
from .forms import FolderForm, FileUploadForm
from django.urls import reverse
from django.contrib import messages


@login_required
def folder_list(request, parent_folder_id=None):
	parent_folder = None
	if parent_folder_id:
		parent_folder = get_object_or_404(Folder, id=parent_folder_id, owner=request.user)



	else:
		# Filter the folders to only include those with no parent folder
		parent_folders = Folder.objects.filter(owner=request.user, parent_folder=None)

	return render(request, 'main/folder_list.html', { 'parent_folder': parent_folder, 'parent_folders': parent_folders})

@login_required
def create_folder(request, parent_folder_id=None):
    parent_folder = None
    if parent_folder_id:
        parent_folder = get_object_or_404(Folder, id=parent_folder_id, owner=request.user)

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.parent_folder = parent_folder
            folder.save()
            return redirect('folder_list')
    else:
        # Filter the folders to only include those with no parent folder
        parent_folders = Folder.objects.filter(owner=request.user, parent_folder=None)
        form = FolderForm()

    return render(request, 'main/create_folder.html', {'form': form,'parent_folder': parent_folder, 'parent_folders': parent_folders})

@login_required
def upload_file(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.folder = folder
            file_instance.owner = request.user
            file_instance.save()
            return redirect('folder_detail', folder_id=folder.id)
    else:
        form = FileUploadForm()

    return render(request, 'main/upload_file.html', {'form': form, 'folder': folder})

@login_required
def folder_detail(request, folder_id=None):
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    else:
        folder = None

    files = folder.files.all() if folder else []
    subfolders = folder.subfolders.all() if folder else []
    form = FolderForm()

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            subfolder = form.save(commit=False)
            subfolder.parent_folder = folder
            subfolder.owner = request.user
            subfolder.save()
            return redirect('folder_detail', folder_id=folder.id)

    return render(request, 'folder_detail.html', {
        'folder': folder,
        'files': files,
        'subfolders': subfolders,
        'form': form
    })



@login_required
def create_subfolder(request, folder_id):
    parent_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            subfolder = form.save(commit=False)
            subfolder.parent_folder = parent_folder
            subfolder.owner = request.user
            subfolder.save()
            return redirect('folder_detail', parent_folder.id)
    else:
        form = FolderForm()

    return redirect('folder_detail', parent_folder.id)






# Delete views
@login_required
def delete_folder(request, folder_id):
    folder_instance = get_object_or_404(Folder, id=folder_id, owner=request.user)
    parent_folder_id = folder_instance.parent_folder.id if folder_instance.parent_folder else None
    folder_instance.delete()
    messages.success(request, 'Folder deleted successfully.')
    return redirect('folder_detail', folder_id=parent_folder_id)

@login_required
def delete_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id, owner=request.user)
    folder_id = file_instance.folder.id
    file_instance.delete()
    messages.success(request, 'File deleted successfully.')
    return redirect('folder_detail', folder_id=folder_id)

# Update views
@login_required
def update_folder(request, folder_id):
    folder_instance = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Folder updated successfully.')
            return redirect('folder_detail', folder_id=folder_instance.id)
    else:
        form = FolderForm(instance=folder_instance)

    return render(request, 'main/update_folder.html', {'form': form, 'folder_instance': folder_instance})

@login_required
def update_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id, owner=request.user)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=file_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'File updated successfully.')
            return redirect('folder_detail', folder_id=file_instance.folder.id)
    else:
        form = FileUploadForm(instance=file_instance)

    return render(request, 'main/update_file.html', {'form': form, 'file_instance': file_instance})
