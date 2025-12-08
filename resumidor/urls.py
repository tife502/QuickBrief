from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.subir_documento, name='subir'),
    path('documento/<int:pk>/', views.ver_documento, name='ver_documento'),
]