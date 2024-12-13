 # views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Folder, File, Key,Trash,UserActivity
from .forms import FolderForm, FileUploadForm,ExtractKeyForm,EnterKeyForm,EditorForm,FileUpdateForm,FolderUpdateForm
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from django.urls import reverse
import pathlib
import re,os
from stegano import lsb
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages
from django.http import HttpResponse
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives import serialization, hashes
from vault.utils import conceal,reveal,calculate_folder_size
from dotenv import load_dotenv
import pytesseract
from django.http import JsonResponse
from PIL import Image 
import requests
import pathlib
from django.core.paginator import Paginator
from pathlib import Path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST,require_GET
import logging
from urllib.parse import urljoin
from django.db.models import Q
from django.core.exceptions import ValidationError
import base64
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_http_methods

import json
from authen.models import Secrets
import pyotp
import qrcode
from django.db.models import Count,Sum
from django.utils import timezone
from datetime import timedelta
  
logger = logging.getLogger(__name__)


load_dotenv()

ID_ENCRYPTION_KEY = str(os.getenv('ID_ENCRYPTION_KEY'))
 
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
        named = request.POST.get('name')

        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.parent_folder = parent_folder
            folder.save()
            UserActivity.objects.create(user=request.user,name=named, activity_type='create-folder')

            return redirect('folder_list')
    else:
        # Filter the folders to only include those with no parent folder
        parent_folders = Folder.objects.filter(owner=request.user, parent_folder=None)
        form = FolderForm()

    return render(request, 'main/create_folder.html', {'form': form,'parent_folder': parent_folder, 'parent_folders': parent_folders})



@login_required
def create_subfolder(request, folder_id):
    parent_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method == 'POST':
        form = FolderUpdateForm(request.POST)
        named = request.POST.get('name')

        if form.is_valid():
            subfolder = form.save(commit=False)
            subfolder.parent_folder = parent_folder
            subfolder.owner = request.user
            subfolder.save()
            UserActivity.objects.create(user=request.user,name=named, activity_type='create-folder')
            return redirect('folder_detail', parent_folder.id)
    else:
        form = FolderForm()

    return redirect('folder_detail', parent_folder.id)

 
# @login_required
# def update_folder(request, folder_id):
#     folder_instance = get_object_or_404(Folder, id=folder_id, owner=request.user)
#     if request.method == 'POST':
#         form = FolderForm(request.POST, instance=folder_instance)
#         named = request.POST.get('name')

#         if form.is_valid():
#             form.save()
#             UserActivity.objects.create(user=request.user,name=named, activity_type='update-folder')
        
#             return JsonResponse({'success': True})
#             messages.success(request, 'Folder updated successfully.')
#             return redirect('folder_detail', folder_id=folder_instance.id)
#         elif request.is_ajax():
#             return JsonResponse({'success': False, 'errors': form.errors})
#     else:
#         form = FolderForm(instance=folder_instance)
    
#     context = {
#         'form': form,
#         'folder_instance': folder_instance,
#         'form_media': form.media
#     }
#     return render(request, 'main/update_folder.html', context)

@login_required
def update_folder(request, folder_id):
    folder_instance = get_object_or_404(Folder, id=folder_id, owner=request.user)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder_instance)
        named = request.POST.get('name')

        if form.is_valid():
            try:
                form.save()
                UserActivity.objects.create(user=request.user, name=named, activity_type='update-folder')
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': str(e)})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = FolderForm(instance=folder_instance)
    
    context = {
        'form': form,
        'folder_instance': folder_instance,
        'form_media': form.media
    }
    return render(request, 'main/update_folder.html', context)



@login_required
def folder_list(request, parent_folder_id=None):
    form = FolderForm(request.POST or None)
    parent_folder = None
    if parent_folder_id:
        parent_folder = get_object_or_404(Folder, id=parent_folder_id, owner=request.user,is_trashed=False)



    else:
        # Filter the folders to only include those with no parent folder
        parent_folders = Folder.objects.filter(owner=request.user, parent_folder=None)

    return render(request, 'main/folder_list.html', { 'form':form,'parent_folder': parent_folder, 'parent_folders': parent_folders})



 
@login_required
def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user, is_trashed=False)
    files = folder.files.filter(is_trashed=False)
    subfolders = folder.subfolders.filter(is_trashed=False)
    form = FolderForm()
    fileorm = FileUploadForm()
    
    size_in_bytes = calculate_folder_size(folder)
    size_in_mb = size_in_bytes  # Note: You might want to convert this to MB
    
    breadcrumb = []
    current_folder = folder
    while current_folder:
        if not current_folder.is_trashed:
            breadcrumb.append(current_folder)
        current_folder = current_folder.parent_folder
    breadcrumb.reverse()
    
    total = files.count() + subfolders.count()
    
    return render(request, 'main/folder_detail.html', {
        'folder': folder,
        'files': files,
        'subfolders': subfolders,
        'form': form,
        'fileorm': fileorm,
        'breadcrumb': breadcrumb,
        'total': total,
        'folsize': size_in_mb,
    })






def dashboard(request):
    user = request.user

    # Vault Statistics
    total_folders = Folder.objects.filter(owner=user).count()
    total_files = File.objects.filter(owner=user).count()
    #total_size = File.objects.filter(owner=user).aggregate(total_size=sum('size'))['total_size']

    # User Activities
    user_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]  # Last 10 activities

    context = {
        'total_folders': total_folders,
        'total_files': total_files,
        #'total_size': total_size,
        'user_activities': user_activities,
    }
    return render(request, 'main/dashboard.html', context)
 
 
@login_required
def dashboard_vault_statistics(request):
    user = request.user
    total_folders = Folder.objects.filter(owner=user).count()
    total_files = File.objects.filter(owner=user).count()
    total_size = File.objects.filter(owner=user).aggregate(Sum('size'))['size__sum'] or 0
    total_downloads = UserActivity.objects.filter(user=user, activity_type='download').count()
    total_shared = UserActivity.objects.filter(user=user, activity_type='share').count()

    # Get file type distribution
    file_types = File.objects.filter(owner=user).values('file_extension').annotate(count=Count('id'))
    file_type_data = [{'label': ft['file_extension'] or 'Unknown', 'value': ft['count']} for ft in file_types]

    # Get folder structure
    folders = list(Folder.objects.filter(owner=user).values('id', 'name', 'parent_folder_id'))
    
    def build_folder_tree(folders, parent_id=None):
        tree = []
        for folder in folders:
            if folder['parent_folder_id'] == parent_id:
                children = build_folder_tree(folders, folder['id'])
                tree.append({
                    'name': folder['name'],
                    'children': children
                })
        return tree

    folder_tree = build_folder_tree(folders)

    context = {
        'total_folders': total_folders,
        'total_files': total_files,
        'total_size': total_size,
        'total_downloads': total_downloads,
        'total_shared':total_shared,
        'file_type_data': json.dumps(file_type_data),
        'folder_tree': json.dumps(folder_tree),
    }
    return render(request, 'main/dashboard_vault_statistics.html', context)

 
@login_required
def dashboard_user_info(request):
    user = request.user

    secrets, created = Secrets.objects.get_or_create(user=user)
    mfa_enabled = bool(secrets.secret)
    

    context = {
        'username': user.username,
            'email': user.email,
            'mfa_enabled': mfa_enabled,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
    }

    return render(request, 'main/dashboard_user_info.html', context)



 
@login_required
def activity_log(request):
    user = request.user
    activities= UserActivity.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'main/activity_log.html', {"activities":activities})
 
@login_required
def dashboard_user_activities(request):
    user = request.user
    last_login = user.last_login
    recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]

    # Activity over time (last 6 months)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    activity_over_time = UserActivity.objects.filter(user=user, timestamp__gte=six_months_ago) \
        .values('timestamp__date') \
        .annotate(count=Count('id')) \
        .order_by('timestamp__date')

    # Prepare data for line chart
    dates = [entry['timestamp__date'].strftime('%Y-%m-%d') for entry in activity_over_time]
    counts = [entry['count'] for entry in activity_over_time]

    # Activity types comparison
    activity_types = UserActivity.objects.filter(user=user) \
        .values('activity_type') \
        .annotate(count=Count('id'))

    # Prepare data for bar chart
    types = [entry['activity_type'] for entry in activity_types]
    type_counts = [entry['count'] for entry in activity_types]

    context = {
        'last_login': last_login,
        'recent_activities': recent_activities,
        'activity_dates': json.dumps(dates),
        'activity_counts': json.dumps(counts),
        'activity_types': json.dumps(types),
        'activity_type_counts': json.dumps(type_counts),
    }

    return render(request, 'main/dashboard_user_activities.html', context)


def dashboard(request):
    return render(request,"main/dashboard.html",{})


@login_required
def tools(request):
    return render(request,"main/tools.html",{})



@login_required
def ocr_tools(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image_file = request.FILES['file']
        image = Image.open(image_file)
        
        # Ensure pytesseract uses the correct executable
        pytesseract.pytesseract.tesseract_cmd = settings.OCR_PATH
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return JsonResponse({'text': text})
    
    form = EditorForm()
    return render(request, "main/ocrtools.html", {'form': form})

def setting(request):
    return render(request,"main/settings.html",{})
   
@login_required
def mfa_setting(request):
    user = request.user
    secrets, created = Secrets.objects.get_or_create(user=user)
    mfa_enabled = bool(secrets.secret)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if 'change_mfa' in request.POST:
            # Generate a new secret
            new_secret = pyotp.random_base32()
            
            # Update the secret in the database
            secrets.secret = new_secret
            secrets.save()

            # Generate the QR code
            totp = pyotp.TOTP(new_secret)
            uri = totp.provisioning_uri(name=user.username, issuer_name='PDV')
            qr = qrcode.make(uri)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return JsonResponse({
                'success': True,
                'qr_code': qr_image_base64
            })

    context = {
        'mfa_enabled': mfa_enabled,
    }
    return render(request, "main/mfasettings.html", context)
 


  
@ensure_csrf_cookie
@login_required
def keys(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    form = ExtractKeyForm(request.POST or None, request.FILES or None)

    out = ""
    qrcode_url = None
    file_instance = None
    out = ""
    if request.method == 'POST':
        if form.is_valid():
            image = form.cleaned_data['steg']
            img_url = urljoin(base_url, f"/media/keys/{image.name}")
            img_url=requests.get(img_url) 
             
             # Use get() to safely retrieve file
            if image:
                
                out = reveal(Image.open(BytesIO(img_url.content)))
                
                return JsonResponse({'out': out})

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q')
        file_id = request.GET.get('file_id')

        if query:
            # Handle search request
            files = File.objects.filter(
                Q(name__icontains=query) & Q(owner=request.user)
            ).values('id', 'name')[:10]  # Limit to 10 results
            return JsonResponse(list(files), safe=False)
        
        elif file_id:
            # Handle file selection request
            file_instance = get_object_or_404(File, id=file_id, owner=request.user)
            qrcode_url = None
            if file_instance.qrcode:
                 
                qrcode_url = urljoin(base_url, f"/media/{file_instance.qrcode.name}")
            
            return JsonResponse({
                'name': file_instance.name,
                'qrcode_url': qrcode_url
            })

        return JsonResponse([], safe=False)

    # Handle non-AJAX requests


    return render(request, "main/keys.html", {
        "form": form,
        "out": out,
        "qrcode_url": qrcode_url,
        "file_instance": file_instance
    })
  

 

 
def folder_description(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    return JsonResponse({'description': folder.description})

 
@login_required
def update_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id, owner=request.user)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=file_instance)
        named = request.POST.get('name')

        if form.is_valid():
            updated_file = form.save(commit=False)
            
            if 'file' in request.FILES:
                # Re-encrypt the new file data
                file_data = request.FILES['file'].read()
                fernet_key = Fernet.generate_key()
                fernet = Fernet(fernet_key)
                encrypted_data = fernet.encrypt(file_data)
                
                # Re-encrypt the new Fernet key
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                public_key = private_key.public_key()
                encrypted_fernet_key = public_key.encrypt(
                    fernet_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Update file properties
                updated_file.encrypted_data = encrypted_data
                updated_file.encrypted_fernet_key = encrypted_fernet_key
                updated_file.file_extension = pathlib.Path(request.FILES['file'].name).suffix
                updated_file.size = request.FILES['file'].size
                
                # Generate new QR code
                private_key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode('utf-8')
                updated_file.qrcode = conceal(private_key_pem, updated_file.name)
                
                # Update icon
                extension = updated_file.file_extension
                nam = "\\" + extension.replace(".", "")
                img = Image.open(str(settings.ICON_PATH) + nam + ".png")
                image_io = BytesIO()
                img.save(image_io, format='PNG')
                image_io.seek(0)
                content_file = ContentFile(image_io.read(), nam + ".png")
                updated_file.icon = content_file

            updated_file.save()
            UserActivity.objects.create(user=request.user,name=named, activity_type='update-file')
            messages.success(request, 'File updated successfully.')
            return redirect('folder_detail', folder_id=updated_file.folder.id)
    else:
        form = FileUploadForm(instance=file_instance)
    
    return render(request, 'main/update_file.html', {'form': form, 'file_instance': file_instance})


@login_required
@require_POST
def delete_item(request):
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')
    print(f"Deleting: {item_type} {item_id} with action {action}")  # Debug print

    if item_type == 'file':
        item = get_object_or_404(File, id=item_id, owner=request.user)
    elif item_type == 'folder':
        item = get_object_or_404(Folder, id=item_id, owner=request.user)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid item type'})

    named = item.name  # Get the name of the file or folder

    if action == 'delete':
        item.delete()
        if item_type == 'file':
            UserActivity.objects.create(user=request.user, name=named, activity_type='delete-file')
        elif item_type == 'folder':
            UserActivity.objects.create(user=request.user, name=named, activity_type='delete-folder')
        return JsonResponse({'status': 'success', 'message': 'Item deleted permanently'})
    elif action == 'trash':
        # Create a Trash object and update the original item's status
        trash_item = Trash.objects.create(
            user=request.user,
            **{item_type: item}
        )
        
        # Update the original item to mark it as trashed
        item.is_trashed = True
        item.save()
        
        if item_type == 'file':
            UserActivity.objects.create(user=request.user, name=named, activity_type='trash-file')
        elif item_type == 'folder':
            UserActivity.objects.create(user=request.user, name=named, activity_type='trash-folder')
            
            # Recursively mark all subfolders and files as trashed
            def mark_subfolder_trashed(folder):
                for subfolder in folder.subfolders.all():
                    subfolder.is_trashed = True
                    subfolder.save()
                    mark_subfolder_trashed(subfolder)
                for file in folder.files.all():
                    file.is_trashed = True
                    file.save()
            
            mark_subfolder_trashed(item)
        
        return JsonResponse({'status': 'success', 'message': 'Item moved to trash'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'})

@login_required
def trash_list(request):
    trash_items = Trash.objects.filter(user=request.user).order_by('-trashed_at')
    return render(request, 'main/trash.html', {'trash_items': trash_items})

@login_required
@require_POST
def restore_item(request):
    trash_id = request.POST.get('trash_id')
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)

    if trash_item.file:
        item = trash_item.file
        item.is_trashed = False
        named=item.name
        item.save()
        UserActivity.objects.create(user=request.user,name=named, activity_type='restore-file')
    elif trash_item.folder:
        item = trash_item.folder
        item.is_trashed = False
        named=item.name
        item.save()
        UserActivity.objects.create(user=request.user,name=named, activity_type='restore-folder')

        # Recursively restore all subfolders and files
        def restore_subfolder(folder):
            for subfolder in folder.subfolders.all():
                subfolder.is_trashed = False
                subfolder.save()
                restore_subfolder(subfolder)
            for file in folder.files.all():
                file.is_trashed = False
                file.save()

        restore_subfolder(item)

    trash_item.delete()
    return JsonResponse({'status': 'success', 'message': 'Item restored from trash'})

 

@login_required
@require_POST
def delete_trash_item(request, trash_id):
    trash_item = get_object_or_404(Trash, id=trash_id, user=request.user)
    if trash_item.file:
        named=trash_item.name
        trash_item.file.delete()
        UserActivity.objects.create(user=request.user,name=named, activity_type='trash-delete-file')

    elif trash_item.folder:
        named=trash_item.name
        trash_item.folder.delete()
        UserActivity.objects.create(user=request.user,name=named, activity_type='trash-delete-folder')
    trash_item.delete()
    return JsonResponse({'status': 'success', 'message': 'Item deleted permanently'})


 

@login_required
def upload_file(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Read file data
            file_data = request.FILES['file'].read()
            uploaded = request.FILES['file']
            pathe = uploaded.name
            size = uploaded.size
            extension = pathlib.Path(pathe).suffix
            nam = "\\" + extension.replace(".", "")
            img = Image.open(str(settings.ICON_PATH) + nam + ".png")
            image_io = BytesIO()
            img.save(image_io, format='PNG')
            image_io.seek(0)
            content_file = ContentFile(image_io.read(), nam + ".png")    
            
            # Generate Fernet key and encrypt data
            fernet_key = Fernet.generate_key()
            fernet = Fernet(fernet_key)
            encrypted_data = fernet.encrypt(file_data)
            
            # Generate a new RSA key pair for this file
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()
            
            # Encrypt the Fernet key with the new public key
            encrypted_fernet_key = public_key.encrypt(
                fernet_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Serialize the private key
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            # Create QR code with concealed private key
            name = pathlib.Path(pathe).stem
            qrcode = conceal(private_key_pem, name)
            

            # Save encrypted data and encrypted key in the database
            named=form.cleaned_data['name']
            UserActivity.objects.create(user=request.user,name=named, activity_type='upload')

            file_instance = File(
                name=named,
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

# @login_required
# def share(request, file_id):
#     try:
#         file_uuid = uuid.UUID(file_id)
#         file = get_object_or_404(File, id=file_uuid, owner=request.user)
#     except ValueError:
#         # Handle invalid UUID
#         return render(request, 'error.html', {'message': 'Invalid file ID'}, status=400)

#     context = {
#         'page_title': f'Share File - {file.name}',
#         'file': file,
#     }
   
#     return render(request, 'share.html', context)

 
@login_required
@require_POST
@csrf_exempt
def decrypt_file(request):
    data = json.loads(request.body)
    key = data.get('key')
    file_id = data.get('file_id')
    
    file_instance = get_object_or_404(File, id=file_id, owner=request.user)
    
    try:
        private_key = serialization.load_pem_private_key(
            key.encode('utf-8'),
            password=None
        )
    except ValueError:
        try:
            private_key = serialization.load_der_private_key(
                base64.b64decode(key),
                password=None
            )
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid key format'}, status=400)

    try:
        fernet_key = private_key.decrypt(
            file_instance.encrypted_fernet_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        fernet = Fernet(fernet_key)
        decrypted_data = fernet.decrypt(file_instance.encrypted_data)
        
        # Encode the decrypted data as base64
        encoded_data = base64.b64encode(decrypted_data).decode('utf-8')
        
        # Store the base64 encoded data in the session
        request.session[f'decrypted_file_{file_id}'] = encoded_data
        
        return JsonResponse({'success': True, 'message': 'File decrypted successfully'})
    except Exception as e:
        print(f"Error decrypting file: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Decryption failed, wrong key'}, status=400)

 

@login_required
def share_file(request, file_id):
    logger.info(f"Sharing file with id: {file_id}")
    file = get_object_or_404(File, id=file_id, owner=request.user)
    share_url = request.build_absolute_uri(reverse('share-file', args=[file_id]))
    
    context = {
        'file': file,
        'share_url': share_url,
        'debug_info': {
            'file_name': file.name,
            'file_size': file.size,
            'owner': file.owner.username,
        }
    }
    named=file.name
    UserActivity.objects.create(user=request.user, name=named,activity_type='share')

    logger.info(f"Rendering share template with context: {context}")
    return render(request, 'main/share.html', context)
 
@login_required
def download_file(request, file_id):
    file = get_object_or_404(File, id=file_id, owner=request.user)
    encoded_data = request.session.get(f'decrypted_file_{file_id}')
    
    if not encoded_data:
        return HttpResponse("File not decrypted or decryption expired", status=400)
    
    # Decode the base64 encoded data
    named=file.name
    UserActivity.objects.create(user=request.user, name=named,activity_type='download')
    
    decrypted_data = base64.b64decode(encoded_data)
    
    response = HttpResponse(decrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file.name}{file.file_extension}"'
    
    # Clear the decrypted data from the session
    del request.session[f'decrypted_file_{file_id}']
    
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



@require_GET
def search_files(request):
    query = request.GET.get('q', '').lower()
    if len(query) < 3:
        return JsonResponse([], safe=False)

    base_dir = settings.BASE_DIR  # Or any other directory you want to search in
    results = []

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if re.search(query, file.lower()):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_dir)
                results.append({
                    'name': file,
                    'path': relative_path
                })
                if len(results) >= 20:  # Limit to 20 results
                    break
        if len(results) >= 20:
            break

    return JsonResponse(results, safe=False)

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
