from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from authen.views import custom_400, custom_403, custom_404, custom_500
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('authen.urls')),
    path("",include('vault.urls')),
    #path('', include('social_django.urls', namespace='social')),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
   

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 

handler400 = custom_400
handler403 = custom_403
handler404 = custom_404
handler500 = custom_500