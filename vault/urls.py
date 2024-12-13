from django.urls import path
from vault import views

urlpatterns = [
    path("",views.cover,name="cover"),
    path('folders/', views.folder_list, name='folder_list'),
    path("main/",views.dashboard,name="main"),
    path('dashboard/vault-statistics/', views.dashboard_vault_statistics, name='dashboard_vault_statistics'),
    path('dashboard/user-activities/', views.dashboard_user_activities, name='dashboard_user_activities'),
    path('dashboard/user-info/', views.dashboard_user_info, name='dashboard_user_info'),
    path('keys/', views.keys, name='keys'),
    path('tools/', views.tools, name='tools'),
    path('tools/ocr-tools/', views.ocr_tools, name='ocr_tools'),
    path('settings/', views.setting, name='settings'),
    path('settings/mfa-settings/', views.mfa_setting, name='mfa_settings'),
    path('folders/', views.folder_search_view, name='folder_search'),
    path('search/', views.search_files, name='search_files'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<str:folder_id>/', views.folder_detail, name='folder_detail'),
    path('folders/<str:folder_id>/upload/', views.upload_file, name='upload_file'),
    path('folders/<str:folder_id>/create_subfolder/', views.create_subfolder, name='create_subfolder'),
    path('folders/<uuid:folder_id>/description/', views.folder_description, name='folder_description'),
    path('folders/update-folder/<str:folder_id>/', views.update_folder, name='update_folder'),
    path('folder-update/<uuid:folder_id>/', views.update_folder, name='update_folder'),
    path('update-file/<str:file_id>/', views.update_file, name='file_update'),
    path('activity_log/',views.activity_log,name="logs"),
    path('delete-item/', views.delete_item, name='delete_item'),
    path('trash/', views.trash_list, name='trash_list'),
    path('trash/restore/', views.restore_item, name='restore_item'),
    path('trash/delete/<uuid:trash_id>/', views.delete_trash_item, name='delete_trash_item'),
    path('decrypt/', views.decrypt_file, name='decrypt_file'),
    path('share/<uuid:file_id>/', views.share_file, name='share-file'),
    path('download/<uuid:file_id>/', views.download_file, name='download_file'),
    path('trash/', views.list_trash, name='list_trash'),
    path('delete-folder-permanent/', views.delete_folder_permanent, name='delete_folder_permanent'),
    path('move-folder-to-trash/', views.move_folder_to_trash, name='move_folder_to_trash'),
    path('move-folder/', views.move_folder, name='move_folder'),
    path('restore-from-trash/', views.restore_from_trash, name='restore_from_trash'),
    path('delete-permanently-from-trash/', views.delete_permanently_from_trash, name='delete_permanently_from_trash'),
 
]



