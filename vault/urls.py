from django.urls import path
from vault import views

urlpatterns = [
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('folders/<int:folder_id>/upload/', views.upload_file, name='upload_file'),
    path('folders/<int:folder_id>/create_subfolder/', views.create_subfolder, name='create_subfolder'),
    path('file/<int:file_id>/update/', views.update_file, name='update_file'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('folder/<int:folder_id>/update/', views.update_folder, name='update_folder'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    ]




