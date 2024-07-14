from stegano import lsb
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO


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