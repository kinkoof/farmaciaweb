from math import radians, cos, sin, asin, sqrt
from django.http import HttpRequest
from django.contrib import messages
from django.shortcuts import redirect, render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# iniciar o banco de dados
if not firebase_admin._apps:
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Create your views here.


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def home(request: HttpRequest):
    user_id = request.session.get('user_id')
    if user_id:
        user_doc = db.collection('usuario').document(user_id).get()
        user_data = user_doc.to_dict()
        user_lat = user_data.get('latitude')
        user_lon = user_data.get('longitude')
    else:
        user_lat, user_lon = None, None

    todas_farmacias = db.collection('farmacias').stream()
    farmacias = []

    for farmacia in todas_farmacias:
        farmacia_data = farmacia.to_dict()
        farmacia_data['id'] = farmacia.id

        if user_lat and user_lon:
            farmacia_lat = farmacia_data.get('latitude')
            farmacia_lon = farmacia_data.get('longitude')

            if farmacia_lat and farmacia_lon:
                try:
                    distancia = haversine(
                        user_lat, user_lon, farmacia_lat, farmacia_lon)
                    farmacia_data['distancia'] = distancia
                except Exception as e:
                    print(f"Erro ao calcular a distância: {e}")
                    farmacia_data['distancia'] = None
            else:
                farmacia_data['distancia'] = None
        else:
            farmacia_data['distancia'] = None

        farmacias.append(farmacia_data)

    if request.GET.get('sort') == 'distance':
        farmacias.sort(key=lambda x: (x['distancia'] is None, x['distancia']))

    context = {
        'farmacias': farmacias,
    }

    return render(request, 'mainpage.html', context)


def farmaciaLoja(request, farmacia_id):
    farmacia_ref = db.collection('farmacias').document(farmacia_id)
    farmacia = farmacia_ref.get().to_dict()

    itens_ref = db.collection('itens').where(
        'farmacia_id', '==', farmacia_id).stream()
    itens = [{'id': item.id, **item.to_dict()} for item in itens_ref]

    return render(request, 'farmaciaLoja.html', {'farmacia': farmacia, 'itens': itens})


def search(request: HttpRequest):
    query = request.GET.get('query')
    user_id = request.session.get('user_id')
    user_lat, user_lon = None, None

    # Obtém a localização do usuário a partir da sessão
    if user_id:
        user_doc = db.collection('usuario').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_lat = user_data.get('latitude')
            user_lon = user_data.get('longitude')

    if not query:
        return render(request, 'search.html', {'itens': []})

    # Busca itens na coleção 'itens'
    todos_itens = db.collection('itens').stream()
    itens_encontrados = []

    for item in todos_itens:
        item_data = item.to_dict()
        item_data['id'] = item.id  # Adiciona o ID do documento
        if query.lower() in item_data.get('nome', '').lower():
            farmacia_id = item_data['farmacia_id']
            farmacia_doc = db.collection('farmacias').document(farmacia_id).get()
            if farmacia_doc.exists:
                farmacia_data = farmacia_doc.to_dict()
                farmacia_data['id'] = farmacia_id

                # Calcula a distância se as coordenadas do usuário e da farmácia estiverem disponíveis
                if user_lat is not None and user_lon is not None and 'latitude' in farmacia_data and 'longitude' in farmacia_data:
                    farmacia_lat = farmacia_data['latitude']
                    farmacia_lon = farmacia_data['longitude']
                    distancia = haversine(float(user_lat), float(user_lon), farmacia_lat, farmacia_lon)
                    farmacia_data['distancia'] = distancia

                item_data['farmacia'] = farmacia_data
                itens_encontrados.append(item_data)

    context = {
        'itens': itens_encontrados,
        'query': query,
    }

    return render(request, 'search.html', context)


def view_carrinho(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Você precisa estar logado para visualizar o carrinho.")
        return redirect('login')

    carrinho_ref = db.collection('usuario').document(user_id).collection('carrinho')
    carrinho_itens = carrinho_ref.stream()
    itens = [{'id': item.id, **item.to_dict()} for item in carrinho_itens]

    # Função para converter preço com vírgula para float
    def convert_price(price_str):
        try:
            # Substitui a vírgula por ponto e converte para float
            return float(price_str.replace(',', '.'))
        except ValueError:
            return 0.0

    # Calcula o valor total
    total = sum(convert_price(item['preco']) * int(item['quantidade']) for item in itens)

    return render(request, 'carrinho.html', {'itens': itens, 'total': total})


def adicionarAoCarrinho(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(
            request, "Você precisa estar logado para adicionar itens ao carrinho.")
        return redirect('login')

    item_doc = db.collection('itens').document(item_id).get()
    if not item_doc.exists:
        messages.warning(request, "Item não encontrado.")
        return redirect('home')

    item_data = item_doc.to_dict()
    farmacia_id = item_data['farmacia_id']

    carrinho_ref = db.collection('usuario').document(
        user_id).collection('carrinho')

    # Verifica se o carrinho já tem itens de uma farmácia diferente
    carrinho_itens = carrinho_ref.stream()
    if carrinho_itens:
        for carrinho_item in carrinho_itens:
            if carrinho_item.to_dict()['farmacia_id'] != farmacia_id:
                messages.warning(
                    request, "Você só pode adicionar itens de uma única farmácia ao carrinho.")
                return redirect('farmaciaLoja', farmacia_id=farmacia_id)

    # Adiciona o item ao carrinho ou atualiza a quantidade
    carrinho_item_ref = carrinho_ref.document(item_id)
    carrinho_item = carrinho_item_ref.get()
    if carrinho_item.exists:
        carrinho_item_ref.update(
            {'quantidade': carrinho_item.to_dict()['quantidade'] + 1})
    else:
        carrinho_item_ref.set({
            'item_id': item_id,
            'nome': item_data['nome'],
            'preco': item_data['preco'],
            'quantidade': 1,
            'imagem_url': item_data.get('imagem_url', ''),
            'farmacia_id': farmacia_id
        })

    messages.success(request, "Item adicionado ao carrinho.")
    return redirect(request.META.get('HTTP_REFERER'), farmacia_id=farmacia_id)


def finalizarPedido(request):
    user_id = request.session.get('user_id')
    if not user_id:
        # Redirecionar para a página de login se o usuário não estiver logado
        return redirect('login')

    # Referência para a subcoleção 'carrinho' do usuário
    carrinho_ref = db.collection('usuario').document(
        user_id).collection('carrinho')

    # Excluir todos os documentos da subcoleção 'carrinho'
    carrinho_docs = carrinho_ref.stream()
    for doc in carrinho_docs:
        doc.reference.delete()

    # Mensagem de sucesso (opcional)
    messages.success(request, "Pedido finalizado com sucesso. Carrinho limpo.")

    # Redirecionar para uma página de confirmação ou outra página relevante
    # Substitua 'pagina_de_confirmacao' pela sua URL desejada
    return redirect('view_carrinho')


def removerDoCarrinho(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Você precisa estar logado para remover itens do carrinho.")
        return redirect('login')

    # Referência para a subcoleção 'carrinho' do usuário
    carrinho_ref = db.collection('usuario').document(user_id).collection('carrinho')

    # Remove o item do carrinho
    carrinho_item_ref = carrinho_ref.document(item_id)
    carrinho_item_ref.delete()

    messages.success(request, "Item removido do carrinho.")
    return redirect('view_carrinho')  # Redireciona de volta para a página do carrinho (altere conforme necessário)
