from django.shortcuts import redirect, render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#iniciar o banco de dados
if not firebase_admin._apps:
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Create your views here.
#carrega o html de login
def login(request):
    return render(request, "login.html")
#carrega o html de cadastro
def cadastro(request):
    return render(request, "cadastro.html")
#carrega o html de cadastro de farmacias
def cadastroFarmacia(request):
    return render(request, "cadastro_farmacia.html")






#envio e verificação das informaçoes de cadastro de usuario
def validaCadastro(request):

    nome = request.POST.get("nome")
    email = request.POST.get("email")
    senha = request.POST.get("senha")

    # Cria o dicionário de dados a ser enviado para o Firestore
    data = {
            "nome": nome,
            "email": email,
            "senha": senha
    }

    # Adiciona um novo documento à coleção 'usuario'
    doc_ref = db.collection('usuario').document()
    doc_ref.set(data)

    return redirect("../login/")

#envio e verificação das informaçoes de cadastro de farmacias
def validaCadastroFarmacia(request):
    emailResponsavel = request.POST.get("emailResponsavel")
    nomeResponsavel = request.POST.get("nomeResponsavel")
    cpf = request.POST.get("cpf")
    senha = request.POST.get("celular")
    celular = request.POST.get("endereco")
    endereco = request.POST.get("nomeFantasia")
    nomeFantasia = request.POST.get("cnpj")
    cnpj = request.POST.get("contaBancaria")
    contaBancaria = request.POST.get("senha")

    # Cria o dicionário de dados a ser enviado para o Firestore
    data = {

        "email": emailResponsavel,
        "nome":nomeResponsavel,
        "cpf":cpf,
        "senha":senha,
        "celular":celular,
        "endereco":endereco,
        "nomeFantasia":nomeFantasia,
        "cnpj":cnpj,
        "contaBancaria":contaBancaria,
    }

    # Adiciona um novo documento à coleção 'farmacia'
    doc_ref = db.collection('farmacias').document()
    doc_ref.set(data)

    return redirect("../login/")

#verificacao da requisicao de login
def validaLogin(request):
    email = request.POST.get("email")
    senha = request.POST.get("senha")
    # Realiza a consulta na coleção 'usuario'
    users_ref = db.collection('usuario').where('email', '==', email).where('senha', '==', senha).stream()

    user_info = None
        # Procura o usuário na coleção 'usuario'
    for user in users_ref:
        print(f"User ID: {user.id} -> {user.to_dict()}")
        user_info = user.to_dict()
        break

    if user_info:
            # Redireciona para a tela principal após o login
            print("Login successful")

            # Salva a seção do usuário
            request.session['user_info'] = user_info
            return redirect("../")

    else:
        print("Login failed: Invalid email or password")

    return redirect("login/")

#logout
def logout(request):
    request.session.flush()
    return redirect('../login/')