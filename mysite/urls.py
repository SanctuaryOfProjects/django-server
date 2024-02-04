"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from project.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', main, name='main'),
    path('administrator/', administrator, name='administrator'),
    path('active/', active, name='active'),
    path('client_orders/', client_orders, name='client_orders'),
    path('add/category/', add_category, name='add_category'),
    path('edit/category/<int:category_id>/', edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),
    path('add/advert/', add_advert, name='add_advert'),
    path('edit/advert/<int:advert_id>/', edit_advert, name='edit_advert'),
    path('delete_advert/<int:advert_id>/', delete_advert, name='delete_advert'),
    path('add/producer/', add_producer, name='add_producer'),
    path('edit/producer/<int:producer_id>/', edit_producer, name='edit_producer'),
    path('delete_producer/<int:producer_id>/', delete_producer, name='delete_producer'),
    path('add/product/', add_product, name='add_product'),
    path('create/', create_order, name='create_order'),
    path('admin_orders/', admin_orders, name='admin_orders'),
    path('order_detail/<int:order_id>/', order_detail, name='order_detail'),
    path('delete_order/<int:order_id>/', delete_order, name='delete_order'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('reviews/', review_list, name='review_list'),
    path('add/review/<int:product_id>/', add_review, name='add_review'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/edit/', product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', product_delete, name='product_delete'),
    path('favorites/', favorite_list, name='favorite_list'),
    path('add_to_favorites/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('ordering/', ordering, name='ordering'),
    path('register/', registration_view, name='register'),
    path('products/<int:category_id>/', product_list, name='product_list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)