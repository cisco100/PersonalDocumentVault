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
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return  redirect(reverse('cover'))
        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

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





CONSTANT_SECRET = 'JBSWY3DPEHPK3PXP7S2QLDPBIDWDOP7T'

@require_http_methods(["GET"])
def pair(request):
    # Use the constant secret
    secret = CONSTANT_SECRET
    
    # Generate a time-based OTP using the secret code
    totp = pyotp.TOTP(secret)
    
    # Create the provisioning URI
    uri = totp.provisioning_uri(name=request.user.username, issuer_name='PDV')
     
    # Generate the QR code
    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Render the QR code within the template
    context = {
        'src': 'data:image/png;base64,' + qr_image_base64,
        'secret': secret  # Pass the secret to the template for display
    }
    return render(request, 'account/mfa/pair.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def verify(request):
    pin = request.POST.get("pin")
    if not pin:
        return JsonResponse({'success': False, 'message': 'PIN not provided'})
    
    # Use the constant secret
    secret = CONSTANT_SECRET
    
    totp = pyotp.TOTP(secret)
    if totp.verify(pin):
        # Verification successful
        return JsonResponse({'success': True, 'message': 'Verification successful'})
        return redirect(to='login')

    else:
        return JsonResponse({'success': False, 'message': 'Verification failed, please try again'})




class LogoutClassView(LogoutView):
    template_name="account/users/logout.html"