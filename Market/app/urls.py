from django.urls import path
from .views import register, login, add_product, get_products, add_to_cart, get_cart, calculate_total

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('add-product/', add_product, name='add_product'),
    path('get-products/', get_products, name='get_products'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('get-cart/', get_cart, name='get_cart'),
    path('calculate-total/', calculate_total, name='calculate_total'),
]
