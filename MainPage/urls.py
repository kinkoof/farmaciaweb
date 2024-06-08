from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name="home"),
    path('famaciaLoja/<str:farmacia_id>/', views.famaciaLoja, name='famaciaLoja'),

]