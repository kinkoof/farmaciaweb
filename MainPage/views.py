from django.http import HttpResponse
from django.shortcuts import render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#iniciar o banco de dados
if not firebase_admin._apps:
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Create your views here.

def home(request):
    todas_farmacias = db.collection('farmacias').stream()
    farmacias = [{'id': farmacia.id, **farmacia.to_dict()} for farmacia in todas_farmacias]

    context = {
        'farmacias': farmacias,
    }

    return render(request, 'mainpage.html', context)


def famaciaLoja(request, farmacia_id):

    farmacia_ref = db.collection('farmacias').document(farmacia_id)
    farmacia = farmacia_ref.get().to_dict()

    itens_ref = db.collection('itens').where('farmacia_id', '==', farmacia_id).stream()
    itens = [item.to_dict() for item in itens_ref]


    return render(request, 'famaciaLoja.html', {'farmacia': farmacia, 'itens': itens})