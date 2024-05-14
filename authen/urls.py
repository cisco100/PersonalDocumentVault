from django.urls import path,include
from authen.views import pair,validate
urlpatterns = [
    path('pair/',pair,name='pair'),
    path('validate/',validate,name='validate'),
    
]
