from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Product,
    Category,
    Galery,
    Review,
    FavoriteProducts,
    Mail,
    Customer,
    Order,
    OrderProduct,
    ShippingAddres,
)


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
    readonly_fields = ("watched",)
    list_editable = ("price", "quantity", "size", "color")
    # Автоматический слаг
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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "created_at")
    readonly_fields = ("author", "text", "created_at")


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "mail")
    readonly_fields = ("user", "mail")


admin.site.register(Galery)
admin.site.register(FavoriteProducts)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("customer", "created_at", "is_completed", "shipping")
    readonly_fields = ("customer", "is_completed", "shipping")
    list_filter = ("customer", "is_completed")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "email")
    readonly_fields = ("user", "first_name", "last_name", "email", "phone")
    list_filter = ("user", )


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("product", "order", "quantity", "added_at")
    readonly_fields = ("product", "order", "quantity", "added_at")
    list_filter = ("product",)


@admin.register(ShippingAddres)
class ShippingAddresAdmin(admin.ModelAdmin):
    list_display = ("customer", "city", "state")
    readonly_fields = ("customer", "order", "city", "state", "street")
    list_filter = ("customer",)
