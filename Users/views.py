from django.shortcuts import redirect, render
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# iniciar o banco de dados
if not firebase_admin._apps:
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Create your views here.

# carrega o html de login
def login(request):
    return render(request, "login.html")

def loginFarmacia(request):
    return render(request, "login_farmacia.html")

# carrega o html de cadastro
def cadastro(request):
    return render(request, "cadastro.html")

# carrega o html de cadastro de farmacias
def cadastroFarmacia(request):
    return render(request, "cadastro_farmacia.html")

# envio e verificação das informaçoes de cadastro de usuario
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

# envio e verificação das informaçoes de cadastro de farmacias
def validaCadastroFarmacia(request):
    if request.method == "POST":
        emailResponsavel = request.POST.get("emailResponsavel")
        nomeResponsavel = request.POST.get("nomeResponsavel")
        cpf = request.POST.get("cpf")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        nomeFantasia = request.POST.get("nomeFantasia")
        cnpj = request.POST.get("cnpj")
        contaBancaria = request.POST.get("contaBancaria")
        senha = request.POST.get("senha")
        senhaConfirm = request.POST.get("senhaConfirm")

        # Verificação de campos obrigatórios
        if not all([emailResponsavel, nomeResponsavel, cpf, celular, endereco, nomeFantasia, cnpj, contaBancaria, senha, senhaConfirm]):
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect("../cadastroFarmacia/")

        if senha != senhaConfirm:
            messages.error(request, "As senhas não conferem.")
            return redirect("../cadastroFarmacia/")

        data = {
            "email": emailResponsavel,
            "nome": nomeResponsavel,
            "cpf": cpf,
            "senha": senha,
            "celular": celular,
            "endereco": endereco,
            "nomeFantasia": nomeFantasia,
            "cnpj": cnpj,
            "contaBancaria": contaBancaria,
        }

        try:
            doc_ref = db.collection('farmacias').document()
            doc_ref.set(data)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("../loginFarmacia/")
        except Exception as e:
            messages.error(request, f"Erro ao realizar cadastro: {e}")
            return redirect("../cadastroFarmacia/")
    else:
        return redirect("../cadastroFarmacia/")

# verificacao da requisicao de login
def validaLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if not email or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect("login/")

        try:
            users_ref = db.collection('usuario').where(
                'email', '==', email).where('senha', '==', senha).stream()

            user_info = None
            for user in users_ref:
                print(f"User ID: {user.id} -> {user.to_dict()}")
                user_info = user.to_dict()
                break

            if user_info:
                request.session['user_info'] = user_info
                request.session['user_type'] = 'usuario'
                return redirect("../../")
            else:
                messages.error(request, "Email ou senha inválidos.")
                return redirect("login/")

        except Exception as e:
            messages.error(request, f"Erro ao tentar fazer login: {e}")
            return redirect("login/")
    else:
        return redirect("login/")

def validaLoginFarmacia(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if not email or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect("../loginFarmacia/")

        try:
            farmacias_ref = db.collection('farmacias').where('email', '==', email).where('senha', '==', senha).stream()

            farmacia_info = None
            for farmacia in farmacias_ref:
                print(f"Farmacia ID: {farmacia.id} -> {farmacia.to_dict()}")
                farmacia_info = farmacia.to_dict()
                break

            if farmacia_info:
                request.session['user_info'] = farmacia_info
                request.session['user_type'] = 'farmacia'
                request.session['farmacia_id'] = farmacia.id
                return redirect("../../")
            else:
                messages.error(request, "Email ou senha inválidos.")
                return redirect("../loginFarmacia/")

        except Exception as e:
            messages.error(request, f"Erro ao tentar fazer login: {e}")
            return redirect("../loginFarmacia/")
    else:
        return redirect("../loginFarmacia/")

# logout
def logout(request):
    request.session.flush()
    return redirect('../login/')

def perfil(request):
    user_info = request.session.get('user_info')
    user_type = request.session.get('user_type')

    if not user_info or user_type != 'usuario':
        messages.error(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    return render(request, 'perfil.html', {'user_info': user_info})

def perfilFarmacia(request):

    user_info = request.session.get('user_info')
    user_type = request.session.get('user_type')

    if not user_info or user_type != 'farmacia':
        messages.error(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    return render(request, 'perfilFarmacia.html', {'user_info': user_info})

def loja(request):
    loja_info = request.session.get('user_info')
    user_type = request.session.get('user_type')
    farmacia_id = request.session.get('farmacia_id')


    if not loja_info or user_type != 'farmacia':
        messages.error(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    itens_ref = db.collection('itens').where('farmacia_id', '==', farmacia_id).stream()
    itens = [item.to_dict() for item in itens_ref]

    return render(request, 'loja.html', {'itens': itens})

def adicionarItem(request):
    farmacia_id = request.session.get('farmacia_id')

    if request.method == "POST":
        nome_item = request.POST.get("nome_item")
        preco_item = request.POST.get("preco_item")
        descricao_item = request.POST.get("descricao_item")

        # Cria o dicionário de dados para o novo item
    data = {
            "nome": nome_item,
            "preco": preco_item,
            "descricao": descricao_item,
            "farmacia_id": farmacia_id
        }

        # Adiciona o novo item à coleção 'itens'
    doc_ref = db.collection('itens').document()
    doc_ref.set(data)

    messages.success(request, "Item adicionado com sucesso.")

    return redirect("../loja/")