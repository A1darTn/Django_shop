from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

CHOICES = (
    ("5", "Отлично"),
    ("4", "Хорошо"),
    ("3", "Нормально"),
    ("2", "Плохо"),
    ("1", "Ужасно"),
)


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
        return reverse("product_page", kwargs={"slug": self.slug})

    def get_first_photo(self):
        if self.images.first():
            return self.images.first().image.url
        else:
            return "https://pubshamrock.com/wp-content/uploads/2023/04/skoro-zdes-budet-foto.jpg"

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


class Review(models.Model):
    """Модель для отзывов"""

    text = models.TextField(verbose_name="Текст комментария")
    grade = models.CharField(
        max_length=20, choices=CHOICES, blank=True, null=True, verbose_name="Оценка"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Продукт"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class FavoriteProducts(models.Model):
    """Избранные товары"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = "Избранный товар"
        verbose_name_plural = "Избранные товары"


class Mail(models.Model):
    """Почтовая рассылка"""

    mail = models.EmailField(unique=True, verbose_name="Почта")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )

    def __str__(self):
        return self.mail

    class Meta:
        verbose_name = "Почта"
        verbose_name_plural = "Почты"


class Customer(models.Model):
    """Контактная информация"""

    user = models.OneToOneField(
        User, models.SET_NULL, blank=True, null=True, verbose_name="Пользователь"
    )
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Почта")
    phone = models.CharField(max_length=55, verbose_name="Контактный номер")

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"


class Order(models.Model):
    """Корзинка"""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_completed = models.BooleanField(default=False, verbose_name="Завершен")
    shipping = models.BooleanField(default=True, verbose_name="Доставка")

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    @property
    def get_cart_total_price(self):
        """Для получения суммы товаров с корзины"""
        order_products = self.ordered.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price
    
    @property
    def get_cart_total_quantity(self):
        """Для получения количества товаров с корзины"""
        order_products = self.ordered.all()
        total_quantity = sum([product.quantity for product in order_products])

        return total_quantity


class OrderProduct(models.Model):
    """Привязка продукта к корзине, строчка товаров"""

    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, verbose_name="Товар"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, related_name="ordered", verbose_name='Корзина'
    )
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"


    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price
    
class ShippingAddres(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Контактная информация')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Корзина')
    city = models.CharField(max_length=255,  verbose_name='Город')
    state = models.CharField(max_length=255, verbose_name='Район')
    street = models.CharField(max_length=255, verbose_name='Улица')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.street
    

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'