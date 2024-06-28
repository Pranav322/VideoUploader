# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('upload/', views.upload_video, name='upload_video'),
#     path('search/', views.search_video, name='search_video'),
# ]


# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_video, name='upload_video'),
    path('search/', views.search_subtitles, name='search_subtitles'),
    # path('generate_presigned_url/', views.generate_presigned_url, name='generate_presigned_url'),
    path('notify_upload_complete/', views.notify_upload_complete, name='notify_upload_complete'),
]
