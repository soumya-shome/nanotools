from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Route for the index page
    path('download', views.download_video, name='download_video'),  # Route for downloading video
    path('download/start', views.start_download, name='start_download'),  # Route for starting download
    path('downloads/<str:filename>', views.download_file, name='download_file'),  # Serve downloaded file
]