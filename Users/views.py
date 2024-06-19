from hashlib import sha256
import secrets
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, storage, firestore, auth, exceptions
from google.cloud import storage
import os
import requests


# Define a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

# iniciar o banco de dados
if not firebase_admin._apps:
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


def login(request):
    return render(request, "login.html")


def loginFarmacia(request):
    return render(request, "login_farmacia.html")


def cadastro(request):
    return render(request, "cadastro.html")


def cadastroFarmacia(request):
    return render(request, "cadastro_farmacia.html")


def validaCadastro(request):
    if request.method == 'POST':
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        senhaConfirm = request.POST.get("senhaConfirm")
        logradouro = request.POST.get("logradouro")
        bairro = request.POST.get("bairro")
        cep = request.POST.get("cep")
        cidade = request.POST.get("cidade")
        estado = request.POST.get("estado")
        numero = request.POST.get("numero")

        # Geocodificação do endereço
        endereco = f"{logradouro}, {numero}, {bairro}, {cidade}, {estado}, {cep}"
        api_key = 'AIzaSyByrpCG-r7Je9DaRR6OmRmHRNIe6KcTG80'
        response = requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json?address={endereco}&key={api_key}')
        data = response.json()

        # Debugging: Verifique o status da resposta
        print("Geocoding API response status:", data['status'])
        print("Geocoding API response:", data)

        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
        else:
            latitude = None
            longitude = None

        # Verificação de campos obrigatórios
        if not all([nome, email, senha, numero, senha, senhaConfirm, estado]):
            messages.warning(request, "Por favor, preencha todos os campos.")
            return redirect("../cadastro/")

        # Verificar se o email já está cadastrado
        users_ref = db.collection('usuario')
        query_ref = users_ref.where('email', '==', email).stream()
        if any(query_ref):
            messages.warning(request, "Este email já está cadastrado.")
            return redirect("../cadastro/")

        if senha != senhaConfirm:
            messages.warning(request, "As senhas não conferem.")
            return redirect("../cadastro/")

        else:
            senha = sha256(senha.encode()).hexdigest()

        # Cria o dicionário de dados a ser enviado para o Firestore
        user_data = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "logradouro": logradouro,
            "bairro": bairro,
            "cep": cep,
            "cidade": cidade,
            "estado": estado,
            "numero": numero,
            "latitude": latitude,
            "longitude": longitude
        }

        # Adiciona um novo documento à coleção 'usuario'
        doc_ref = db.collection('usuario').document()
        doc_ref.set(user_data)

        return redirect("../login/")
    return render(request, 'cadastro.html')


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
        imagem = request.FILES.get("imagem")
        logradouro = request.POST.get("logradouro")
        bairro = request.POST.get("bairro")
        cep = request.POST.get("cep")
        cidade = request.POST.get("cidade")
        estado = request.POST.get("estado")
        numero = request.POST.get("numero")

        # Geocodificação do endereço
        endereco = f"{logradouro}, {bairro}, {cidade}, {estado}, {cep}"
        api_key = 'AIzaSyByrpCG-r7Je9DaRR6OmRmHRNIe6KcTG80'
        response = requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json?address={endereco}&key={api_key}')
        data = response.json()

        # Debugging: Verifique o status da resposta
        print("Geocoding API response status:", data['status'])
        print("Geocoding API response:", data)

        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
        else:
            latitude = None
            longitude = None

        # Verificação de campos obrigatórios
        if not all([emailResponsavel, nomeResponsavel, cpf, celular, endereco, nomeFantasia, cnpj, contaBancaria, senha, senhaConfirm]):
            messages.warning(request, "Por favor, preencha todos os campos.")
            return redirect("../cadastroFarmacia/")

        farmacias_ref = db.collection('farmacias')
        query_ref = farmacias_ref.where(
            'email', '==', emailResponsavel).stream()
        if any(query_ref):
            messages.warning(request, "Este email já está cadastrado.")
            return redirect("../cadastroFarmacia/")

        if senha != senhaConfirm:
            messages.warning(request, "As senhas não conferem.")
            return redirect("../cadastroFarmacia/")

        else:
            senha = sha256(senha.encode()).hexdigest()

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
            "logradouro": logradouro,
            "bairro": bairro,
            "cep": cep,
            "cidade": cidade,
            "estado": estado,
            "numero": numero,
            "latitude": latitude,
            "longitude": longitude
        }

        if imagem:
            try:
                # Initialize Firebase Storage client
                storage_client = storage.Client()

                # Define the bucket name
                bucket_name = "farmacia-1fdf6.appspot.com"

                # Get a reference to the bucket
                bucket = storage_client.bucket(bucket_name)

                # Upload the file to Cloud Storage
                blob = bucket.blob(imagem.name)
                blob.upload_from_file(imagem)

                # Get the URL of the uploaded file
                imagem_url = blob.public_url

                # Add the image URL to the data
                data["imagem_perfil"] = imagem_url
            except Exception as e:
                messages.warning(
                    request, f"Erro ao fazer upload da imagem: {e}")
                return redirect("../cadastroFarmacia/")

        try:
            doc_ref = db.collection('farmacias').document()
            doc_ref.set(data)

            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("../loginFarmacia/")
        except Exception as e:
            messages.warning(request, f"Erro ao realizar cadastro: {e}")
            return redirect("../cadastroFarmacia/")
    else:
        return redirect("../cadastroFarmacia/")


def validaLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        senha = sha256(senha.encode()).hexdigest()

        if not email or not senha:
            messages.warning(request, "Por favor, preencha todos os campos.")
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
                request.session['user_id'] = user.id

                return redirect("../../")
            else:
                messages.warning(request, "Email ou senha inválidos.")
                return redirect("login/")

        except Exception as e:
            messages.warning(request, f"Erro ao tentar fazer login: {e}")
            return redirect("login/")
    else:
        return redirect("login/")


def validaLoginFarmacia(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if not email or not senha:
            messages.warning(request, "Por favor, preencha todos os campos.")
            return redirect("../loginFarmacia/")

        try:
            farmacias_ref = db.collection('farmacias').where(
                'email', '==', email).where('senha', '==', senha).stream()

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
                messages.warning(request, "Email ou senha inválidos.")
                return redirect("../loginFarmacia/")

        except Exception as e:
            messages.warning(request, f"Erro ao tentar fazer login: {e}")
            return redirect("../loginFarmacia/")
    else:
        return redirect("../loginFarmacia/")


def logout(request):
    request.session.flush()
    return redirect('../login/')


def perfil(request):
    user_info = request.session.get('user_info')
    user_type = request.session.get('user_type')
    id = request.session.get('user_id')

    if not user_info or user_type != 'usuario':
        messages.warning(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    return render(request, 'perfil.html', {'user_info': user_info, 'id': id})


def perfilFarmacia(request):

    user_info = request.session.get('user_info')
    user_type = request.session.get('user_type')
    farmacia_id = request.session.get('farmacia_id')

    if not user_info or user_type != 'farmacia':
        messages.warning(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    itens_ref = db.collection('itens').where(
        'farmacia_id', '==', farmacia_id).stream()
    itens = [item.to_dict() for item in itens_ref]

    # Adicione a URL da imagem ao dicionário 'itens'
    for item in itens:
        # Se 'imagem_url' estiver presente no item, adicione a URL ao dicionário
        if 'imagem_url' in item:
            item['imagem_url'] = item['imagem_url']

    return render(request, 'perfilFarmacia.html', {'user_info': user_info, 'itens': itens})


def loja(request):
    loja_info = request.session.get('user_info')
    user_type = request.session.get('user_type')
    farmacia_id = request.session.get('farmacia_id')

    if not loja_info or user_type != 'farmacia':
        messages.warning(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    itens_ref = db.collection('itens').where(
        'farmacia_id', '==', farmacia_id).stream()
    itens = [item.to_dict() for item in itens_ref]

    # Adicione a URL da imagem ao dicionário 'itens'
    for item in itens:
        # Se 'imagem_url' estiver presente no item, adicione a URL ao dicionário
        if 'imagem_url' in item:
            item['imagem_url'] = item['imagem_url']

    return render(request, 'loja.html', {'itens': itens})


def adicionarItem(request):

    farmacia_id = request.session.get('farmacia_id')

    if request.method == "POST":
        nome_item = request.POST.get("nome_item")
        preco_item = request.POST.get("preco_item")
        descricao_item = request.POST.get("descricao_item")
        imagem = request.FILES.get("imagem")

        data = {
            "nome": nome_item,
            "preco": preco_item,
            "descricao": descricao_item,
            "farmacia_id": farmacia_id
        }

        if imagem:
            # Initialize Firebase Storage client
            storage_client = storage.Client()

            # Define the bucket name
            bucket_name = "farmacia-1fdf6.appspot.com"

            # Get a reference to the bucket
            bucket = storage_client.bucket(bucket_name)

            # Upload the file to Cloud Storage
            blob = bucket.blob(imagem.name)
            blob.upload_from_file(imagem)

            # Get the URL of the uploaded file
            imagem_url = blob.public_url

            # Add the image URL to the data
            data["imagem_url"] = imagem_url

        # Adicionar o novo item à coleção no Firestore
        doc_ref = db.collection('itens').document()
        doc_ref.set(data)

        messages.success(request, "Item adicionado com sucesso.")

        return redirect("../loja/")
    else:
        # Handle GET request, if needed
        pass


def editarUsuario(request):
    user_info = request.session.get('user_info')
    user_type = request.session.get('user_type')
    id = request.session.get('user_id')

    if not user_info or user_type != 'usuario':
        messages.warning(
            request, "Você precisa estar logado para acessar esta página.")
        return redirect("../login/")

    if request.method == "POST":
        # Obter dados do formulário
        novo_email = request.POST.get("email")
        novo_nome = request.POST.get("nome")
        nova_senha = request.POST.get("senha")
        novo_cep = request.POST.get("cep")
        novo_estado = request.POST.get("estado")
        nova_cidade = request.POST.get("cidade")
        novo_logradouro = request.POST.get("logradouro")
        novo_numero = request.POST.get("numero")

        # Atualizar os dados do usuário no banco de dados
        try:
            db.collection('usuario').document(id).update({
                'email': novo_email,
                'nome': novo_nome,
                'senha': nova_senha,
                'cep': novo_cep,
                'estado': novo_estado,
                'cidade': nova_cidade,
                'logradouro': novo_logradouro,
                'numero': novo_numero,
            })

            # Atualizar os dados da sessão
            user_info['email'] = novo_email
            user_info['nome'] = novo_nome
            user_info['senha'] = nova_senha
            user_info['cep'] = novo_cep
            user_info['estado'] = novo_estado
            user_info['cidade'] = nova_cidade
            user_info['logradouro'] = novo_logradouro
            user_info['numero'] = novo_numero
            request.session['user_info'] = user_info

            messages.success(request, "Dados atualizados com sucesso.")
            return redirect("/auth/perfil/")
        except Exception as e:
            messages.warning(
                request, f"Erro ao tentar atualizar os dados: {e}")
            print(id)
            return redirect("/auth/perfil/")
    else:
        return render(request, 'editar_usuario.html', {'user_info': user_info})


def redefinirSenha(request):
    return render(request, "redefinirSenha.html")


def email_para_redefinir_senha(request):

    email = request.POST.get("email")
    users_ref = db.collection('usuario')
    query_ref = users_ref.where('email', '==', email).stream()

    if not(query_ref):
            messages.warning(request, "Este email não está cadastrado.")
            return redirect("../cadastro/")

    if user.reset_password_token:
        return HttpResponse("Link de redefinição de senha já utilizado ou expirado.")

    # Gerar um token exclusivo
    reset_token = secrets.token_urlsafe(16)

    # Salvar o token no usuário
    user.reset_password_token = reset_token
    user.save()

    reset_link = f"http://127.0.0.1:8000/auth/reset_password_template/{user.id}/{reset_token}"

    send_mail(
        "Password change",
        f"Para redefinir sua senha, clique no link a seguir: {reset_link}",
        "myasthenia.email@gmail.com",
        [resetemail],
        fail_silently=False,
    )

    # Redirecione para a página de login após o envio do e-mail
    return redirect("../login")
