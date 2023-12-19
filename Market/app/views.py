from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Product, ShoppingCart, CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator


def get_product_price(product_id):
    product = get_object_or_404(Product, id=product_id)
    return product.price


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.pk) + str(timestamp) +
                str(user.is_active)
        )


token_generator = TokenGenerator()


def generate_token(user_id, role):
    user = User.objects.get(pk=user_id)
    return token_generator.make_token(user)


@csrf_exempt
@api_view(['POST'])
def register(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    hashed_password = make_password(password)

    try:
        user = CustomUser.objects.create_user(username=username, password=password, role=role)
        token = generate_token(user.id, role)
        return JsonResponse({'token': token}, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return JsonResponse({'error': 'User with this username already exists'}, status=status.HTTP_400_BAD_REQUEST)
@csrf_exempt
@api_view(['POST'])
def login(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    user = CustomUser.objects.get(username=username)

    if check_password(password, user.password):
        token = generate_token(user.id, user.role)
        return JsonResponse({'token': token})
    else:
        return JsonResponse({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def add_product(request):
    if request.user.role != 'admin':
        raise PermissionDenied('� ��� ��� ���� ��� ���������� ����� ��������')

    data = request.data
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    images = [ContentFile(image, name=f'image_{index}.png') for index, image in enumerate(data.getlist('images'))]

    product = Product.objects.create(name=name, description=description, price=price)
    product.images.set(images)

    return JsonResponse({'id': product.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    # Serialize 'products' to return the response


@api_view(['POST'])
def add_to_cart(request):
    data = request.data
    product_id = data.get('productId')
    quantity = data.get('quantity')
    user_id = request.user.id

    existing_cart, created = ShoppingCart.objects.get_or_create(user_id=user_id)

    if not created:
        existing_products = existing_cart.products
        existing_products.append({'productId': product_id, 'quantity': quantity})
        existing_cart.save()

    return JsonResponse({'success': True})


@api_view(['GET'])
def get_cart(request):
    user_id = request.user.id
    cart = get_object_or_404(ShoppingCart, user_id=user_id)
    # Serialize 'cart' to return the response


@api_view(['GET'])
def calculate_total(request):
    user_id = request.user.id
    cart = get_object_or_404(ShoppingCart, user_id=user_id)
    products = cart.products or []

    total = sum(product['quantity'] * get_product_price(product['productId']) for product in products)
    return JsonResponse({'total': total})