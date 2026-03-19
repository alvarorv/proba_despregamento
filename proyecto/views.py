import datetime
from django.http import HttpResponse
from django.shortcuts import render

from store.models import Product

LEGAL_INFO = {
    "owner_name": "Álvaro",
    "business_name": "Álvaro",
    "nif": "",
    "address": "Rúa de San Clemente, s/n, 15705 Santiago de Compostela",
    "email": "a24alvarorv@iessanclemente.net",
    "phone": "600 123 4562",
    "registry": "No aplica",
    "domain": "alvaro.software",
}


def home(request):

    products = Product.objects.all().filter(is_available=True).order_by('created_date')



    context = {
        'products': products,
 
    }
    return render(request, 'home.html', context) 


def aviso_legal(request):
    context = {
        "legal": LEGAL_INFO,
    }
    return render(request, "legal/aviso_legal.html", context)


def declaracion_accesibilidad(request):
    context = {
        "legal": LEGAL_INFO,
        "accessibility_date": datetime.date.today().strftime("%d/%m/%Y"),
    }
    return render(request, "legal/declaracion_accesibilidad.html", context)


def politica_cookies(request):
    context = {
        "legal": LEGAL_INFO,
    }
    return render(request, "legal/politica_cookies.html", context)
