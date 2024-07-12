# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addpic/', views.detect, name='detect'),
    path('rec/', views.recognize, name='recognize'),
    path('rec-img/', views.recognize_image, name='recognize_image'),
]