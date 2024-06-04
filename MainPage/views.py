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
    farmacias = [farmacia.to_dict() for farmacia in todas_farmacias]

    context = {
        'farmacias': farmacias,
    }

    return render(request, 'mainpage.html', context)
