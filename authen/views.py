from django.shortcuts import render,redirect
import requests
import os
import time
from PIL import Image 
from io import BytesIO
from bs4 import BeautifulSoup
from django.urls import reverse,reverse_lazy
import uuid
from django.http import JsonResponse
from authen.forms import PinCodeForm
from authen.models import Secrets
from authen.utils import secretcode
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView,PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
import qrcode
import pyotp
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import base64
from django.views.decorators.http import require_POST,require_http_methods
 

 
class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'account/users/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('cover'))
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Generate and store the initial secret for MFA
            secret = pyotp.random_base32()
            Secrets.objects.create(user=user, secret=secret)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            
            # Store the secret in the session for use in the pair view
            request.session['mfa_secret'] = secret
            
            return redirect(to='pair')
        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
    
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'account/users/password_reset.html'
    email_template_name = 'account/users/password_reset_email.html'
    subject_template_name = 'account/users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'account/users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'account/users/profile.html', {'user_form': user_form, 'profile_form': profile_form})





  

#@login_required
def pair(request):
    # Retrieve the secret from the session
    secret = request.session.get('mfa_secret')
    
    if not secret:
        # If there's no secret in the session, get it from the database
        secrets = Secrets.objects.get(user=request.user)
        secret = secrets.secret

    if not secret:
        messages.error(request, 'Error retrieving MFA secret. Please contact support.')
        return redirect('settings')

    # Generate the QR code
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=request.user.username, issuer_name='PDV')
    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    context = {
        'src': f'data:image/png;base64,{qr_image_base64}'
    }

    # Clear the secret from the session after use
    if 'mfa_secret' in request.session:
        del request.session['mfa_secret']

    return render(request, 'account/mfa/pair.html', context)
 

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def verify(request):
    pin = request.POST.get("pin")
    if not pin:
        return JsonResponse({'success': False, 'message': 'PIN not provided'})
    
    try:
        # Retrieve the secret for the current user
        user_secret = Secrets.objects.get(user=request.user)
        secret = user_secret.secret
        
        if not secret:
            return JsonResponse({'success': False, 'message': 'MFA not set up for this user'})
        
        totp = pyotp.TOTP(secret)
        if totp.verify(pin):
            # Verification successful
            return JsonResponse({'success': True, 'message': 'Verification successful'})
        else:
            return JsonResponse({'success': False, 'message': 'Verification failed, please try again'})
    
    except Secrets.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'MFA not set up for this user'})



class LogoutClassView(LogoutView):
    next_page = reverse_lazy('login')

    template_name="account/users/logout.html"


def custom_400(request, exception):
    return render(request, 'errors/400.html', status=400)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)