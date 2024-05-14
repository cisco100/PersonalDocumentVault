from django.urls import path,include
from vault.views import cover_view,folder_list,create_folder,upload_file,folder_detail
urlpatterns = [
    path("",cover_view,name="cover"),
    path("list/",folder_list,name="list"),
    path("create/",create_folder,name="create"),
    path("upload/",upload_file,name="upload"),
    path("detail/",folder_detail,name="detail"),
]
