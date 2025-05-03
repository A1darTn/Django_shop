from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=155, verbose_name="Наименование категории")
    image = models.ImageField(
        upload_to="categories/", null=True, blank=True, verbose_name="Изображение"
    )
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="subcategories",
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Категория: pk={self.pk}, title={self.title}"

    def get_parent_category_photo(self):
        """Для получения картинки родительской категории"""
        if self.image:
            return self.image.url
        else:
            return "https://pubshamrock.com/wp-content/uploads/2023/04/skoro-zdes-budet-foto.jpg"

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    price = models.FloatField(verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    watched = models.PositiveIntegerField(
        default=0, verbose_name="Количество просмотров"
    )
    quantity = models.PositiveIntegerField(
        default=0, verbose_name="Количество товара на складе"
    )
    description = models.TextField(
        default="Скоро здесь будет описание...", verbose_name="Описание товара"
    )
    info = models.TextField(
        default="Дополнительная информация о товаре", verbose_name="Информация о товаре"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="products",
    )
    slug = models.SlugField(unique=True, null=True)
    size = models.PositiveIntegerField(default=30, verbose_name="Размер в мм")
    color = models.CharField(
        max_length=30, default="Серебро", verbose_name="Цвет/Материал"
    )

    def get_absolute_url(self):
        return reverse('product_page', kwargs={'slug': self.slug})

    def get_first_photo(self):
        if self.images.first():
            return self.images.first().image.url
        else:
            return 'https://pubshamrock.com/wp-content/uploads/2023/04/skoro-zdes-budet-foto.jpg'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Товар: pk={self.pk}, title={self.title}, price={self.price}"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Galery(models.Model):
    image = models.ImageField(upload_to="products/", verbose_name="Изображение")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Галерея товаров"
