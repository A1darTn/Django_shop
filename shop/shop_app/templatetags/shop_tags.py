from django import template
from django.template.defaulttags import register as range_register

from shop_app.models import Category, FavoriteProducts


register = template.Library()


@register.simple_tag()
def get_subcategories(category):
    return Category.objects.filter(parent=category)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            "title": "Цена",
            "sorters": [("price", "По возрастанию"), ("-price", "По убыванию")],
        },
        {
            "title": "Цвет",
            "sorters": [("color", "От А до Я"), ("-color", ("От Я до А"))],
        },
        {
            "title": "Размер",
            "sorters": [("size", "По возрастанию"), ("-size", "По убыванию")],
        },
    ]

    return sorters


@range_register.filter
def get_positive_range(value):
    return range(int(value))


@range_register.filter
def get_negative_range(value):
    return range(5 - int(value))


@register.simple_tag()
def get_favorite_products(user):
    fav = FavoriteProducts.objects.filter(user=user)
    products = [i.product for i in fav]

    return products
