from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField("Название категории", max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Advert(models.Model):
    heading = models.CharField("Заголовок", max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    photo = models.FileField("Фото товара", upload_to="adv/")
    date = models.DateField(verbose_name="Дата")

    class Meta:
        verbose_name_plural = "Реклама"

    def __str__(self):
        return self.heading


class Producer(models.Model):
    name = models.CharField("Название производителя", max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    description = models.TextField("Описание производителя")
    photo = models.FileField("Фото", upload_to="photos/")

    class Meta:
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField("Название товара", max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    article = models.CharField("Артикул товара", max_length=50, unique=True, blank=True)
    photo = models.FileField("Фото товара", upload_to="product_photos/")
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, verbose_name="Производитель")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=0)
    description = models.TextField("Описание товара")
    instruction = models.FileField("Инструкция по использованию", upload_to="instructions/", blank=True, null=True)
    quantity = models.PositiveIntegerField("Количество на складе")
    recipe_required = models.BooleanField("Требуется рецепт", default=False)
    in_stock = models.BooleanField("В наличии", default=True)

    class Meta:
        verbose_name_plural = "Препараты"

    def __str__(self):
        return f'{self.name}-{self.article}'

class Review(models.Model):
    subject = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField("Отзыв")
    stars = models.PositiveIntegerField("Оценка", default=5)
    

    class Meta:
        verbose_name_plural = "Отзывы"

class Favorite(models.Model):
    subject = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Избранное"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartProduct')
    
    class Meta:
        verbose_name_plural = "Корзина"

    def __str__(self):
        return f"Cart for {self.user}"

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = "Компонент корзины"

    def __str__(self):
        return f"{self.quantity} шт x {self.product.name} в {self.cart}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, verbose_name = "Ф.И.О")
    phone_number = models.CharField(max_length=20, null=True, verbose_name = "Номер телефона")
    email = models.EmailField(null=True, verbose_name = "Email")
    delivery_address = models.CharField(max_length=255, null=True)
    recipe = models.FileField("Рецепт", upload_to="recipe_photos/", null=True)
    comments = models.TextField(blank=True, null=True, verbose_name = "Комментарий")
    PAYMENT_CHOICES = [
        ('kaspi', 'Выставить счет в Kaspi'),
        ('card', 'Банковская карта'),
        ('cash', 'Наличными курьеру'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Способ оплаты", blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now, null=True, verbose_name = "Дата заказа")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name = "Итоговая сумма")
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('accepted', 'Принят'),
        ('canceled', 'Отменен'),
        ('done', 'Доставлен')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name = "Статус")

    def __str__(self):
        return f"Заказ #{self.id} от {self.full_name}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = "Заказ"

    def __str__(self):
        return f"{self.quantity} шт x {self.product.name} в заказе {self.order}"
