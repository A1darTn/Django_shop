from django.shortcuts import render, redirect
from django.views.generic import ListView, DeleteView

from .models import Category, Product
# Create your views here.


class Index(ListView):
    """Главная страница"""
    model = Product
    extra_context = {'title': 'Главная страница'}
    template_name = 'shop/index.html'