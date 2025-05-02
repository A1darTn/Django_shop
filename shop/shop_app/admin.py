from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Product, Category, Galery


# Register your models here.
class GaleryInline(admin.TabularInline):
    fk_name = "product"
    model = Galery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "get_products_count")
    prepopulated_fields = {"slug": ("title",)}

    def get_products_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return "0"

    get_products_count.short_description = "Количество товаров"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "category",
        "quantity",
        "price",
        "created_at",
        "size",
        "color",
        "get_photo",
    )
    list_editable = ("price", "quantity", "size", "color")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title", "price")
    list_display_links = ("pk", "title")
    inlines = (GaleryInline,)

    def get_photo(self, obj):
        if obj.images.all():
            return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75">')
        else:
            return "-"

    get_photo.short_description = "Фото"


admin.site.register(Galery)
