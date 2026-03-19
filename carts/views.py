from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect

from store.models import Product
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem, Order, OrderItem

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
        

    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (21 * total) / 100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (21 * total) / 100
            grand_total = total + tax
    except ObjectDoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
    context = {
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def payment(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('cart')

    cart_items = CartItem.objects.select_related('product').filter(cart=cart, is_active=True)
    if not cart_items:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('cart')

    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = int((21 * total) / 100)
    grand_total = total + tax

    with transaction.atomic():
        product_ids = [ci.product_id for ci in cart_items]
        products = {
            p.id: p
            for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }
        for cart_item in cart_items:
            product = products.get(cart_item.product_id)
            if not product or product.stock < cart_item.quantity:
                messages.error(request, f'Sin stock suficiente para {cart_item.product.product_name}.')
                return redirect('cart')

        order = Order.objects.create(
            user=request.user,
            total=total,
            tax=tax,
            grand_total=grand_total,
        )

        for cart_item in cart_items:
            product = products[cart_item.product_id]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price,
            )
            product.stock -= cart_item.quantity
            product.save(update_fields=['stock'])

        cart_items.delete()

    return render(request, 'store/payment.html')
