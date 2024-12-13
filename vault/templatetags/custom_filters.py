from atexit import register
from django import template
from cryptography.fernet import Fernet
from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()
ID_ENCRYPTION_KEY = str(os.getenv('ID_ENCRYPTION_KEY'))

register = template.Library()

@register.filter
def replaceBlank(value,stringVal = ""):
    value = str(value).replace(stringVal, '')
    return value

@register.filter
def encryptdata(value):
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value = fernet.encrypt(str(value).encode())
    return value
# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def format_extension(value):
    return value[1:].upper()
