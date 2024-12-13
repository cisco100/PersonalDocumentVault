from stegano import lsb
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models import Sum
from django.db.models.functions import Coalesce
from vault.models import Folder,File



def conceal(key,name):
	secret=lsb.hide(settings.IMG_PATH,key)
	image_io=BytesIO()
	write=secret.save(image_io,format='PNG')
	image_io.seek(0)
	content_file=ContentFile(image_io.read(),name+".png")
	return content_file





def reveal(qrcode):
	show=lsb.reveal(qrcode)
	return show




def calculate_folder_size(folder):
     
    def get_subfolder_ids(folder_id):
        subfolder_ids = list(Folder.objects.filter(parent_folder_id=folder_id).values_list('id', flat=True))
        for subfolder_id in subfolder_ids.copy():
            subfolder_ids.extend(get_subfolder_ids(subfolder_id))
        return subfolder_ids

    # Get all subfolder IDs including the current folder
    all_folder_ids = [folder.id] + get_subfolder_ids(folder.id)
    
    # Assuming you have a File model related to Folder
    total_size = File.objects.filter(folder_id__in=all_folder_ids).aggregate(
        total_size=Coalesce(Sum('size'), 0)
    )['total_size']

    return total_size
 