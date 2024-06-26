from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.perfil, name="perfil"),
    path('editarUsuario/', views.editarUsuario, name="editar_usuario"),
    path('perfilFarmacia/', views.perfilFarmacia, name="perfilFarmacia"),
    path('editarFarmacia/', views.editarFarmacia, name="editar_farmacia"),

    path('loja/', views.loja, name="loja"),
    path('adcionarItem/', views.adicionarItem, name="adicionarItem"),

    path('login/', views.login, name="login"),
    path('validaLogin', views.validaLogin, name="valida_login"),

    path('loginFarmacia/', views.loginFarmacia, name="login_farmacia"),
    path('validaloginFarmacia/', views.validaLoginFarmacia, name="valida_login_farmacia"),

    path('cadastro/', views.cadastro, name="cadastro"),
    path('validaCadastro/', views.validaCadastro, name="valida_cadastro"),

    path('cadastroFarmacia/', views.cadastroFarmacia, name="cadastro_farmacia"),
    path('validaCadastroFarmacia/', views.validaCadastroFarmacia, name="valida_cadastro_farmacia"),

    path('logout/', views.logout, name="logout"),

    path('redefinirSenha/', views.view_redefinir_senha, name="redefinirSenha"),
    path('email_para_redefinir_senha/', views.email_para_redefinir_senha, name="email_para_redefinir_senha"),
    path('alterarsenha/<str:id>/<str:reset_token>/', views.redefinir_senha, name="redefinir_senha"),



]