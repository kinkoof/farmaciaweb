from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('validaLogin', views.validaLogin, name="valida_login"),

    path('cadastro/', views.cadastro, name="cadastro"),
    path('validaCadastro/', views.validaCadastro, name="valida_cadastro"),

    path('cadastroFarmacia/', views.cadastroFarmacia, name="cadastro_farmacia"),
    path('validaCadastroFarmacia/', views.validaCadastroFarmacia, name="valida_cadastro_farmacia"),

    path('logout/', views.logout, name="logout"),


]