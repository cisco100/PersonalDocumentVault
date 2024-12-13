from django.urls import path,include,re_path
from authen.views import pair,verify
from django.contrib.auth import views as auth_views
from authen.views import CustomLoginView, ResetPasswordView, ChangePasswordView
from .views import  profile, RegisterView,LogoutClassView
from authen.forms import LoginForm


urlpatterns = [
    path('mfa/pair/',pair,name='pair'),
    path('mfa/verify/',verify,name='verify'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),

    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='account/users/login.html',
                                           authentication_form=LoginForm), name='login'),

    path('logout/', LogoutClassView.as_view(), name='logout'),

    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='account/users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='account/users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password-change/', ChangePasswordView.as_view(), name='password_change'),

   
] 