"""
Vistas principales del proyecto Porvoz
"""
from django.shortcuts import render


def index(request):
    """
    Vista de inicio - Dashboard principal
    """
    return render(request, 'porvoz/index.html')

