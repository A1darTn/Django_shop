from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import IntegrityError

from .models import Category, Product, Review, FavoriteProducts, Mail
from .forms import LoginForm, RegistrationForm, ReviewForm, ShippingForm, CustomerForm
from .utils import CartForAuthenticatedUser, get_cart_data

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
        data = (
            Product.objects.all()
            .exclude(slug=self.kwargs["slug"])
            .filter(category=product.category)[:5]
        )
        context["products"] = data
        context["reviews"] = Review.objects.filter(product=product).order_by("-pk")

        if self.request.user.is_authenticated:
            context["review_form"] = ReviewForm

        return context


def login_registration(request):
    context = {
        "title": "Войти или зарегистрироваться",
        "login_form": LoginForm,
        "registration_form": RegistrationForm,
    }

    return render(request, "shop/login_registration.html", context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)

        return redirect("index")
    else:
        messages.error(request, "Неверное имя или пароль")

        return redirect("login_registration")


def registration(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Аккаунт успешно создан")
    else:
        # messages.error(request, 'Что-то пошло не так')
        for error in form.errors:
            messages.error(request, form.errors[error].as_text())

    return redirect("login_registration")


def user_logout(requset):
    logout(requset)

    return redirect("index")


def save_review(request, product_pk):
    """Сохранение отзыва"""
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(pk=product_pk)
        review.product = product
        review.save()

        return redirect("product_page", product.slug)


def save_favorite_product(requset, product_slug):
    """Добавление или удаление избранных товаров"""
    user = requset.user if requset.user.is_authenticated else None
    product = Product.objects.get(slug=product_slug)
    favorite_products = FavoriteProducts.objects.filter(user=user)
    if user:
        if product in [i.product for i in favorite_products]:
            fav_product = FavoriteProducts.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            FavoriteProducts.objects.create(user=user, product=product)

        next_page = requset.META.get("HTTP_REFERER", "category_detail")

        return redirect(next_page)


class FavoriteProductsView(ListView, LoginRequiredMixin):
    """Вывод избранных товаров"""

    model = FavoriteProducts
    context_object_name = "products"
    template_name = "shop/favorite_product.html"
    login_url = "user_registration"

    def get_queryset(self):
        """Получение товара конкретного пользователя"""
        favs = FavoriteProducts.objects.filter(user=self.request.user)
        products = [i.product for i in favs]

        return products


def save_subscribers(request):
    """Почтовые адресса"""
    email = request.POST.get("email")
    user = request.user if request.user.is_authenticated else None
    if email:
        try:
            Mail.objects.create(mail=email, user=user)
            messages.success(request, "Вы успешно подписались!")
        except IntegrityError:
            messages.error(request, "Вы уже подписаны")
        return redirect("index")


def send_email_to_subscribers(request):
    from shop import settings

    from django.core.mail import send_mail

    if request.method == "POST":
        text = request.POST.get("text")
        mail_lists = Mail.objects.all()
        for email in mail_lists:
            send_mail(
                subject="У нас новая акция",
                message=text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

    context = {"title": "Отправка расслыки"}

    return render(request, "shop/send_email.html", context)


def cart(request):
    """Страничка корзины"""

    cart_info = get_cart_data(request)
    context = {
        "title": "Корзинка",
        "order": cart_info["order"],
        "order_products": cart_info["order_products"],
        "cart_total_quantity": cart_info["cart_total_quantity"],
    }

    return render(request, "shop/cart.html", context)


def to_cart(request, product_id, action):
    """Добавлять товар в корзину"""
    try:
        if request.user.is_authenticated:
            CartForAuthenticatedUser(request, product_id, action)
            return redirect("cart")
        else:
            messages.error(
                request,
                "Авторизируйтесь или зарегистрируйтесь, чтобы совершать покупки",
            )
            return redirect("login_registration")
    except:
        messages.error(request, "Товар отсутвует на складе")
        return redirect("index")


def checkout(request):
    cart_info = get_cart_data(request)
    context = {
        "title": "Оформление заказа",
        "order": cart_info["order"],
        "order_products": cart_info["order_products"],
        "cart_total_quantity": cart_info["cart_total_quantity"],
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm(),
    }

    return render(request, 'shop/checkout.html', context)