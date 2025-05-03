from random import randint
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import Category, Product

# Create your views here.


class Index(ListView):
    """Главная страница"""

    model = Product
    context_object_name = "categories"
    extra_context = {"title": "Главная страница"}
    template_name = "shop/index.html"

    def get_queryset(self):
        """Вывод родительской категории"""
        categories = Category.objects.filter(parent=None)
        return categories

    def get_context_data(self, **kwargs):
        """Вывод на страницу доп элементов"""
        context = super().get_context_data()  # context = {}
        context["top_products"] = Product.objects.order_by("-watched")[:8]
        return context


class SubCategories(ListView):
    """Вывод категорий на отдельной странички"""

    model = Product
    context_object_name = "products"
    template_name = "shop/category_page.html"

    def get_queryset(self):
        """Получение всех товаров подкатегорий"""
        if type_field := self.request.GET.get("type"):
            products = Product.objects.filter(category__slug=type_field)
            return products

        parent_category = Category.objects.get(slug=self.kwargs["slug"])
        subcategories = parent_category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories).order_by("?")

        if sort_field := self.request.GET.get("sort"):
            products = products.order_by(sort_field)
        return products

    def get_context_data(self, **kwargs):
        """Дополнительные элементы"""
        context = super().get_context_data(**kwargs)
        parent_category = Category.objects.get(slug=self.kwargs["slug"])
        context["category"] = parent_category
        context["title"] = parent_category.title
        return context


class ProductPage(DetailView):
    """Вывод товара на отдельной страничке"""

    model = Product
    context_object_name = "product"
    template_name = "shop/product_page.html"

    def get_context_data(self, **kwargs):
        """Вывод на страничку доп элементов"""
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(slug=self.kwargs["slug"])
        context["title"] = product
        # products = Product.objects.filter(category=product.category)

        # data = []
        # for _ in range(5):
        #     random_index = randint(0, len(products) - 1)
        #     random_product = products[random_index]
        #     if random_product not in data and str(random_product) != product.title:
        #         data.append(random_product)

        # context['products'] = data
        data = (
            Product.objects.all()
            .exclude(slug=self.kwargs["slug"])
            .filter(category=product.category)[:5]
        )
        context["products"] = data

        return context
