from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name="home"),
    path('farmaciaLoja/<str:farmacia_id>/',views.farmaciaLoja, name='farmaciaLoja'),
    path('search/', views.search, name='search'),
    path('carrinho/', views.view_carrinho, name="view_carrinho"),


]
