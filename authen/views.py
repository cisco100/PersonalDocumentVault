from django.shortcuts import render,redirect
import requests
import os
import time
from bs4 import BeautifulSoup
from django.urls import reverse
import uuid
from authen.forms import PinCodeForm
from authen.utils import secretcode

APPNAME="PDV"
SECRETCODE=secretcode()
def pair(request):
	print(SECRETCODE)
	src=''
	if request.user.is_authenticated and not request.user.is_anonymous:
		
		APPINFO=str(request.user.username).upper()

		url=f'https://www.authenticatorapi.com/pair.aspx?AppName={APPNAME}&AppInfo={APPINFO}&SecretCode={SECRETCODE}'
		req= requests.get(url)
		soup=BeautifulSoup(req.text,'html.parser')
		img=soup.find('img')
		src=img.get('src')
	else:
		print("something is wrong")
	return render(request,'account/mfa/pair.html',{"src":src})
print(SECRETCODE)

def validate(request):
    form=PinCodeForm(request.POST or None)
    msg=None
    print(SECRETCODE)
    if request.method=="POST":
        if form.is_valid():
            pin=form.cleaned_data.get("pin")
            url=f'https://www.authenticatorapi.com/Validate.aspx?Pin={pin}&SecretCode={SECRETCODE}'
            req=requests.get(url)
            if req.text=='True':
            	msg="<p style='color:green;'> <b>Validation Successful</b></p>"
            	time.sleep(5)
            	return redirect(reverse('cover'))
            elif req.text=='False':
            	msg="<p style='color:red;'> <b>Validation Failed,please try again</b></p>"
 
    return render(request,'account/mfa/validate.html',{'msg':msg,'form':form})

