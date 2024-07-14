# views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Folder, File, Key,Trash
from .forms import FolderForm, FileUploadForm,ExtractKeyForm,EnterKeyForm
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from django.urls import reverse
import pathlib
from stegano import lsb
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages
from django.http import HttpResponse
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from vault.utils import conceal,reveal
from dotenv import load_dotenv
import os
from django.http import JsonResponse
from PIL import Image 
import requests
import pathlib
from django.core.paginator import Paginator
from pathlib import Path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
load_dotenv()

ID_ENCRYPTION_KEY = str(os.getenv('ID_ENCRYPTION_KEY'))



@login_required
def folder_list(request, parent_folder_id=None):
    form = FolderForm(request.POST or None)
    parent_folder = None
    if parent_folder_id:
        parent_folder = get_object_or_404(Folder, id=parent_folder_id, owner=request.user)



    else:
		# Filter the folders to only include those with no parent folder
        parent_folders = Folder.objects.filter(owner=request.user, parent_folder=None)

    return render(request, 'main/folder_list.html', { 'form':form,'parent_folder': parent_folder, 'parent_folders': parent_folders})

@login_required
def cover(request):
    return render(request,"main/cover.html")


@login_required
def create_folder(request, parent_folder_id=None):
    form = FolderForm(request.POST or None)
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
def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    files = folder.files.all()
    subfolders = folder.subfolders.all()
    form = FolderForm()
    fileorm = FileUploadForm()

    #send private key to  user download view
    form_key=EnterKeyForm(request.POST or None)

    if request.method=="POST":
    	if form_key.is_valid():
    		request.session['entered_key']=request.POST['key']

    breadcrumb = []
    current_folder = folder
    while current_folder:
        breadcrumb.append(current_folder)
        current_folder = current_folder.parent_folder
    breadcrumb.reverse()

    total=int(files.count())+int(subfolders.count())
    
    return render(request, 'main/folder_detail.html', {
        'folder': folder,
        'files': files,
        'subfolders': subfolders,
        'form': form,
        'fileorm': fileorm,
        'breadcrumb':breadcrumb,
        'total':total,
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




# @login_required
# def keys(request):
#     file_instance = get_object_or_404(File, owner=request.user)
#     qrcode=file_instance.qrcode #file_instance.qrcode
#     form = ExtractKeyForm(request.POST or None)
#     out=""
#     if request.method == 'POST':
#         if form.is_valid():
#             image = request.FILES['steg']
#             out=conceal(str(image.name))
#     return render(request,"main/keys.html",{"form":form,"out":out,"qrcode":qrcode})



@ensure_csrf_cookie
@login_required
def keys(request):
    file_instance = get_object_or_404(File, owner=request.user)
    qrcode = file_instance.qrcode
    form = ExtractKeyForm(request.POST or None, request.FILES or None)
    out = ""

    if request.method == 'POST':
       

        if form.is_valid():
            image = form.cleaned_data['steg']
            img_url=requests.get(f"http://127.0.0.1:8000/media/keys/{image.name}") 
             
             # Use get() to safely retrieve file
            if image:
                
                out = reveal(Image.open(BytesIO(img_url.content)))
                
                return JsonResponse({'out': out})

    # Debugging output
    print("Out value:", out)  # Check if out is populated

    return render(request, "main/keys.html", {"form": form, "out": out, "qrcode": qrcode})


@login_required
def dashboard(request):
    return render(request,"main/dashboard.html")

@login_required
def tools(request):
    return render(request,"main/tools.html")

@login_required
def setting(request):
    return render(request,"main/settings.html")



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


''' Write error pages'''

@login_required
def upload_file(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)


    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Read file data
            file_data = request.FILES['file'].read()
            uploaded = request.FILES['file']
            pathe=uploaded.name
            size=uploaded.size
            extension=pathlib.Path(pathe).suffix

            nam=str("\\")+str(extension.replace(".",""))
            img=Image.open(str(settings.ICON_PATH)+nam+str(".png"))
            image_io=BytesIO()
            write=img.save(image_io,format='PNG')
            image_io.seek(0)
            content_file=ContentFile(image_io.read(),nam+".png")    
            
            
            # Encrypt data with Fernet
            fernet_key = Fernet.generate_key()
            fernet = Fernet(fernet_key)
            encrypted_data = fernet.encrypt(file_data)

            # Get the user's public key
            user_keys = get_object_or_404(Key, user=request.user)
            public_key = serialization.load_pem_public_key(user_keys.public_key.encode('utf-8'))

            # Encrypt the Fernet key with RSA
            encrypted_fernet_key = public_key.encrypt(
                fernet_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            private_key = serialization.load_pem_private_key(user_keys.private_key.encode('utf-8'),password=None)
            
            private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
                ).decode('utf-8')
            name=pathlib.Path(pathe).stem

            qrcode=conceal(private_key_pem,name)


            # Save encrypted data and encrypted key in the database
            file_instance = File(
                name=form.cleaned_data['name'],
                #description=forms.cleaned_data['description'],
                encrypted_data=encrypted_data,
                encrypted_fernet_key=encrypted_fernet_key,
                file_extension=extension,
                size=size,
                folder=folder,
                qrcode=qrcode,
                icon=content_file,
                owner=request.user
            )
            file_instance.save()
            return redirect('folder_detail', folder_id=folder.id)
    else:
        form = FileUploadForm()

    return render(request, 'main/upload_file.html', {'form': form, 'folder': folder})

def share(request,id=None):
    context['page_title'] = 'Share File'
    if not id is None:
        key = ID_ENCRYPTION_KEY
        fernet = Fernet(key)
        id = base64.urlsafe_b64decode(id)
        id = fernet.decrypt(id).decode()
        file = File.objects.get(id = id)
        context['file'] = file
        context['page_title'] += str(" - " + file.name)
   
    return render(request, 'share.html',context)







@login_required
def download_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id, owner=request.user)

    key=request.session.pop('entered_key',None)    

    private_key = serialization.load_pem_private_key(
        key.encode('utf-8'),
        password=None
    )

    #find a way to be able to drag and drop the file to a form to reveal
    # on download popup shows,inputkey 
    # qrcode=file_instance.qrcode
    # private=conceal(qrcode.name)

    # private_key = serialization.load_pem_private_key(
    #     private.encode('utf-8'),
    #     password=None
    # )

    # print(private_key)

    # Decrypt the Fernet key with RSA
    fernet_key = private_key.decrypt(
        file_instance.encrypted_fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    


    # Decrypt the file data with Fernet
    fernet = Fernet(fernet_key)
    decrypted_data = fernet.decrypt(file_instance.encrypted_data)

    response = HttpResponse(decrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_instance.name+file_instance.file_extension}"'
    return response






def folder_search_view(request):
    query = request.GET.get('q', '')
    if query:
        parent_folders = Folder.objects.filter(
            Q(parent_folder__isnull=True) & 
            (Q(name__icontains=query) | Q(description__icontains=query))
        )
    else:
        parent_folders = Folder.objects.filter(parent_folder__isnull=True)
    
    context = {
        'parent_folders': parent_folders,
        'query': query,
    }
    return render(request, 'main/search.html', context)

#-------------------------------------------------------------------------------------------------------

@login_required
def list_trash(request):
    trash_items = Trash.objects.filter(user=request.user).order_by('-deleted_at')
    return render(request, 'main/trash.html', {'trash_items': trash_items})

@login_required
def move_to_trash(request, item_type, item_id):
    if item_type == 'file':
        item = get_object_or_404(File, id=item_id)
    elif item_type == 'folder':
        item = get_object_or_404(Folder, id=item_id)
    else:
        return HttpResponseForbidden("Invalid item type")

    if item.owner != request.user:
        return HttpResponseForbidden("You do not have permission to delete this item")

    Trash.objects.create(
        user=request.user,
        file=item if item_type == 'file' else None,
        folder=item if item_type == 'folder' else None,
        deleted_at=timezone.now()
    )
    item.delete()

    return redirect('list_trash')

@login_required
def restore_from_trash(request, trash_id):
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)

    if trash_item.file:
        trash_item.file.save()  # Restores the file
    if trash_item.folder:
        trash_item.folder.save()  # Restores the folder

    trash_item.delete()
    return redirect('list_trash')

@login_required
def delete_permanently(request, trash_id):
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)

    if trash_item.file:
        trash_item.file.delete()
    if trash_item.folder:
        trash_item.folder.delete()

    trash_item.delete()
    return redirect('list_trash')


 

# @login_required
# def delete_folder(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
#     parent_folder_id = folder.parent_folder.id if folder.parent_folder else None
    
#     # Move to trash instead of deleting
#     Trash.objects.create(
#         user=request.user,
#         folder=folder,
#         deleted_at=timezone.now()
#     )
#     folder.is_deleted = True
#     folder.save()
    
#     messages.success(request, 'Folder moved to trash successfully.')
#     return redirect('folder_detail', folder_id=parent_folder_id) if parent_folder_id else redirect('folder_list')

# @login_required
# def delete_file(request, file_id):
#     file = get_object_or_404(File, id=file_id, owner=request.user)
#     folder_id = file.folder.id
    
#     # Move to trash instead of deleting
#     Trash.objects.create(
#         user=request.user,
#         file=file,
#         deleted_at=timezone.now()
#     )
#     file.is_deleted = True
#     file.save()
    
#     messages.success(request, 'File moved to trash successfully.')
#     return redirect('folder_detail', folder_id=folder_id)

# @login_required
# def list_trash(request):
#     trash_items = Trash.objects.filter(user=request.user).order_by('-deleted_at')
#     return render(request, 'main/trash.html', {'trash_items': trash_items})

# @login_required
# def restore_from_trash(request, trash_id):
#     trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)

#     if trash_item.file:
#         trash_item.file.is_deleted = False
#         trash_item.file.save()
#     if trash_item.folder:
#         trash_item.folder.is_deleted = False
#         trash_item.folder.save()

#     trash_item.delete()
#     messages.success(request, 'Item restored successfully.')
#     return redirect('list_trash')

# @login_required
# def delete_permanently(request, trash_id):
#     trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)

#     if trash_item.file:
#         trash_item.file.delete()
#     if trash_item.folder:
#         trash_item.folder.delete()

#     trash_item.delete()
#     messages.success(request, 'Item deleted permanently.')
#     return redirect('list_trash')
 
# @login_required
# def move_to_trash(request, item_type, item_id):
#     if item_type == 'file':
#         item = get_object_or_404(File, id=item_id, owner=request.user)
#     elif item_type == 'folder':
#         item = get_object_or_404(Folder, id=item_id, owner=request.user)
#     else:
#         return HttpResponseForbidden("Invalid item type")

#     Trash.objects.create(
#         user=request.user,
#         file=item if item_type == 'file' else None,
#         folder=item if item_type == 'folder' else None,
#         deleted_at=timezone.now()
#     )
#     item.is_deleted = True
#     item.save()

#     messages.success(request, f'{item_type.capitalize()} moved to trash successfully.')
#     return redirect('list_trash')





@login_required 
@require_POST
def delete_folder_permanent(request):
    folder_id = request.POST.get('folderId')
    try:
        folder = Folder.objects.get(id=folder_id, owner=request.user)
        folder.delete()
        return JsonResponse({'success': True})
    except Folder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Folder not found'})
 
@login_required
@require_POST
def move_folder(request):
    folder_id = request.POST.get('folderId')
    destination_id = request.POST.get('destinationFolderId')
    try:
        folder = Folder.objects.get(id=folder_id, owner=request.user)
        destination = Folder.objects.get(id=destination_id, owner=request.user)
        folder.parent_folder = destination
        folder.save()
        return JsonResponse({'success': True})
    except Folder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Folder not found'})


@login_required 
@require_POST
def delete_folder_permanent(request):
    folder_id = request.POST.get('folderId')
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.delete()
    return JsonResponse({'success': True})

@login_required 
@require_POST
def move_folder_to_trash(request):
    folder_id = request.POST.get('folderId')
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    Trash.objects.create(user=request.user, folder=folder)
    return JsonResponse({'success': True})

@login_required 
@require_POST
def restore_from_trash(request):
    trash_id = request.POST.get('trashId')
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)
    
    if trash_item.folder:
        folder = trash_item.folder
        folder.parent_folder = None  # You might want to restore it to a specific location
        folder.save()
    elif trash_item.file:
        file = trash_item.file
        file.folder = None  # You might want to restore it to a specific location
        file.save()
    
    trash_item.delete()
    return JsonResponse({'success': True})

@login_required 
@require_POST
def delete_permanently_from_trash(request):
    trash_id = request.POST.get('trashId')
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)
    
    if trash_item.folder:
        trash_item.folder.delete()
    elif trash_item.file:
        trash_item.file.delete()
    
    trash_item.delete()
    return JsonResponse({'success': True})




 

def list_trash(request):
    trash_items = Trash.objects.filter(user=request.user).order_by('-deleted_at')
    
    # Pagination
    paginator = Paginator(trash_items, 20)  # Show 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'trash_list.html', context)
 #--------------------------------------Errors--------------------

# def handler404(request, exception):
#     return render(request, 'errors/404.html', status=404)

# def handler500(request):
#     return render(request, 'errors/500.html', status=500)

# def handler403(request, exception):
#     return render(request, 'errors/403.html', status=403)

# def handler400(request, exception):
#     return render(request, 'errors/400.html', status=400)
