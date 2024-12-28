from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Route for the index page
    path('generate_qr', views.generate_qr, name='generate_qr'),  # Route for QR generation
]
