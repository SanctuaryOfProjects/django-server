from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Max, Min, Avg


def main(request):
    categories = Category.objects.all()
    latest_adverts = Advert.objects.order_by('-date')[:3]
    return render(request, 'main.html', {'categories': categories, 'latest_adverts': latest_adverts})

# Create your views here.
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def administrator(request):
    categories = Category.objects.all()
    categories_stats = Category.objects.annotate(
        product_count=Count('product'),
        max_price=Max('product__price'),
        min_price=Min('product__price'),
        review_count=Count('product__review'),
        avg_stars=Avg('product__review__stars')
    )
    context = {'categories_stats': categories_stats,
               'categories': categories}
    return render(request, 'administrator.html', context)

def active(request):
    categories = Category.objects.all()
    return render(request, 'active.html', {'categories': categories})

def product_list(request, category_id):
    categories = Category.objects.all()
    category = get_object_or_404(Category, id=category_id)
    manufacturers = Producer.objects.all()
    products = Product.objects.filter(category=category)

    # Existing filters
    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(producer_id=manufacturer_id)

    max_price = request.GET.get('price')
    if max_price:
        products = products.filter(price__lte=max_price)

    # New filters
    if 'recipe_required' in request.GET:
        products = products.filter(recipe_required=True)

    if 'in_stock' in request.GET:
        products = products.filter(in_stock=True)
    
    paginator = Paginator(products, 6)  # Show 6 products per page
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'product_list.html', {
        'categories': categories,
        'category': category,  # Pass the category to the template
        'manufacturers': manufacturers,
        'products': products,
    })

@login_required
def product_detail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(subject=product)
    is_favorite = Favorite.objects.filter(subject=product, user=request.user).exists()

    return render(request, 'product_detail.html', {'categories': categories, 'product': product, 'reviews': reviews, 'is_favorite': is_favorite})

def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list', category_id=product.category.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_edit.html', {'form': form, 'product': product})

def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category_id = product.category.id
    product.delete()
    return redirect('product_list', category_id=category_id)

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    products = [favorite.subject for favorite in favorites]

    # Convert the list to a queryset
    product_queryset = Product.objects.filter(id__in=[product.id for product in products])

    # Get all categories and producers
    all_categories = Category.objects.all()
    all_producers = Producer.objects.all()

    # Apply filters
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    max_price = request.GET.get('price')
    prescription_required = request.GET.get('recipe_required')
    in_stock = request.GET.get('in_stock')

    if category_id:
        product_queryset = product_queryset.filter(category_id=category_id)

    if manufacturer_id:
        product_queryset = product_queryset.filter(producer_id=manufacturer_id)

    if max_price:
        product_queryset = product_queryset.filter(price__lte=max_price)

    if prescription_required:
        product_queryset = product_queryset.filter(recipe_required=True)

    if in_stock:
        product_queryset = product_queryset.filter(in_stock=True)

    return render(request, 'favorites.html', {'products': product_queryset, 'all_categories': all_categories, 'all_producers': all_producers})

@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Проверяем, не добавлен ли уже товар в избранное
    if not Favorite.objects.filter(subject=product, user=request.user).exists():
        Favorite.objects.create(subject=product, user=request.user)

    return redirect('product_list', category_id=product.category.id)

def review_list(request):
    categories = Category.objects.all()
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'review_list.html', {'categories': categories, 'reviews': reviews})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        stars = request.POST.get('stars')
        
        Review.objects.create(subject=product, user=request.user, feedback=feedback, stars=stars)

    return redirect('product_detail', product_id=product_id)

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'create_order.html', {'form': form})


def add_category(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 6)
    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form, 'categories': categories,})

def edit_category(request, category_id):
    categories = Category.objects.all()
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('add_category')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_edit.html', {'form': form, 'category': category, 'categories': categories})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('add_category')

def add_advert(request):
    categories = Category.objects.all()
    adverts = Advert.objects.all()
    if request.method == 'POST':
        form = AdvertForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = AdvertForm()

    return render(request, 'add_advert.html', {'form': form, 'adverts': adverts, 'categories': categories,})

def edit_advert(request, advert_id):
    categories = Category.objects.all()
    advert = get_object_or_404(Advert, pk=advert_id)
    if request.method == 'POST':
        form = AdvertForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            return redirect('add_advert')
    else:
        form = AdvertForm(instance=advert)

    return render(request, 'advert_edit.html', {'form': form, 'advert': advert, 'categories': categories})

def delete_advert(request, advert_id):
    advert= get_object_or_404(Advert, id=advert_id)
    advert.delete()
    return redirect('add_advert')

def add_producer(request):
    categories = Category.objects.all()
    producers = Producer.objects.all()
    if request.method == 'POST':
        form = ProducerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = ProducerForm()

    return render(request, 'add_producer.html', {'form': form, 'producers': producers, 'categories': categories})

def edit_producer(request, producer_id):
    categories = Category.objects.all()
    producer = get_object_or_404(Producer, pk=producer_id)
    if request.method == 'POST':
        form = ProducerForm(request.POST, request.FILES, instance=producer)
        if form.is_valid():
            form.save()
            return redirect('add_producer')  # Redirect to your producer list view
    else:
        form = ProducerForm(instance=producer)

    return render(request, 'producer_edit.html', {'form': form, 'producer': producer, 'categories': categories})

def delete_producer(request, producer_id):
    producer = get_object_or_404(Producer, id=producer_id)
    producer.delete()
    return redirect('add_producer')


def admin_orders(request):
    categories = Category.objects.all()
    return render(request, 'admin_orders.html', {'categories': categories})

def add_product(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form, 'products': products, 'categories': categories})



@login_required
def client_orders(request):
    categories = Category.objects.all()
    user = request.user
    orders = Order.objects.filter(user=user)
    
    context = {'user': user, 'orders': orders, 'categories': categories}
    return render(request, 'client_orders.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    try:
        cart = user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=user)

    cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)

    if not created:
        if cart_product.quantity < product.quantity:
            cart_product.quantity += 1
            cart_product.save()
        else:
            messages.warning(request, f"{product.name} is out of stock.")

    return redirect('product_list', category_id=product.category.id)

@login_required
def cart(request):
    categories = Category.objects.all()
    user = request.user
    try:
        cart = user.cart
        cart_products = CartProduct.objects.filter(cart=cart)
        total_price = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)
    except Cart.DoesNotExist:
        cart_products = []
        total_price = 0

    context = {'cart_products': cart_products, 'user': user, 'total_price': total_price, 'categories': categories}
    return render(request, 'cart.html', context)

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    try:
        cart = user.cart
    except Cart.DoesNotExist:
        return redirect('product_list', category_id=product.category.id)

    cart_product = CartProduct.objects.filter(cart=cart, product=product).first()

    if cart_product and cart_product.quantity > 1:
        cart_product.quantity -= 1
        cart_product.save()
    elif cart_product:
        cart_product.delete()

    return redirect('product_list', category_id=product.category.id)

@login_required
def ordering(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            order = Order(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                delivery_address=form.cleaned_data['delivery_address'],
                comments=form.cleaned_data['comments'],
                payment_method=form.cleaned_data['payment_method']

            )
            order.save()

            try:
                user = request.user
                cart = user.cart
                cart_products = CartProduct.objects.filter(cart=cart)
                total_price = 0

                for cart_product in cart_products:
                    order_product = OrderProduct(order=order, product=cart_product.product, quantity=cart_product.quantity)
                    order_product.save()
                    total_price += cart_product.product.price * cart_product.quantity

                order.total_price = total_price
                order.save()

                cart.products.clear()

                return redirect('client_orders')
            except Cart.DoesNotExist:
                messages.warning(request, "Корзина пуста.")
                return redirect('ordering')
    else:
        form = OrderForm(user=request.user)

    user = request.user
    try:
        cart = user.cart
        cart_products = CartProduct.objects.filter(cart=cart)
        total_price = sum(cart_product.product.price * cart_product.quantity for cart_product in cart_products)
    except Cart.DoesNotExist:
        cart_products = []
        total_price = 0

    context = {'form': form, 'user': user, 'cart_products': cart_products, 'total_price': total_price, 'categories': categories}
    return render(request, 'ordering.html', context)

def admin_orders(request):
    categories = Category.objects.all()
    orders = Order.objects.all()
    context = {'orders': orders, 'categories': categories}
    return render(request, 'admin_orders.html', context)

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, f"Заказ {order_id} был удален.")
    return redirect('admin_orders')

def order_detail(request, order_id):
    categories = Category.objects.all()
    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('admin_orders')
    else:
        form = OrderStatusForm(instance=order)

    context = {'order': order, 'form': form, 'categories': categories}
    return render(request, 'order_detail.html', context)