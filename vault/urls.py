 from django.urls import path
from vault import views

urlpatterns = [
    path("",views.cover,name="cover"),
    path('folders/', views.folder_list, name='folder_list'),
    path("main/",views.dashboard,name="main"),
    path('keys/', views.keys, name='keys'),
    path('tools/', views.tools, name='tools'),
    path('settings/', views.setting, name='settings'),
    path('folders/', views.folder_search_view, name='folder_search'),
    path('search/', views.search_files, name='search_files'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<str:folder_id>/', views.folder_detail, name='folder_detail'),
    path('folders/<str:folder_id>/upload/', views.upload_file, name='upload_file'),
    path('folders/<str:folder_id>/create_subfolder/', views.create_subfolder, name='create_subfolder'),
    path('file/<str:file_id>/update/', views.update_file, name='update_file'),
    path('file/<str:file_id>/delete/', views.delete_file, name='delete_file'),
    path('folder/<str:folder_id>/update/', views.update_folder, name='update_folder'),
    path('folder/<str:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('file/<str:file_id>/download/', views.download_file, name='download_file'),
    path(r'share/<str:id>', views.share, name='share-id'),
    path('share/', views.share, name='share-file'),
    # path('trash/', views.list_trash, name='list_trash'),
    # path('trash/move/<str:item_type>/<uuid:item_id>/', views.move_to_trash, name='move_to_trash'),
    # path('trash/restore/<uuid:trash_id>/', views.restore_from_trash, name='restore_from_trash'),
    # path('trash/delete/<uuid:trash_id>/', views.delete_permanently, name='delete_permanently'),
    # path('move-to-trash/<str:item_type>/<str:item_id>/', views.move_to_trash, name='move_to_trash'),
    path('trash/', views.list_trash, name='list_trash'),
    path('delete-folder-permanent/', views.delete_folder_permanent, name='delete_folder_permanent'),
    path('move-folder-to-trash/', views.move_folder_to_trash, name='move_folder_to_trash'),
    path('move-folder/', views.move_folder, name='move_folder'),
    path('restore-from-trash/', views.restore_from_trash, name='restore_from_trash'),
    path('delete-permanently-from-trash/', views.delete_permanently_from_trash, name='delete_permanently_from_trash'),
 
]



