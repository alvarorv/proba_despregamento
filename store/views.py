from django.shortcuts import render
from carts.models import CartItem
from store.models import Product
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
import random

# Lorem ipsum text for generating reviews
LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat 
non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis 
unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, 
eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo."""

AVATARS = [
    'images/avatars/avatar1.jpg',
    'images/avatars/avatar2.jpg',
    'images/avatars/avatar3.jpg',
]

REVIEWER_NAMES = [
    'Maria González',
    'Juan Pérez',
    'Carlos López',
    'Ana Martínez',
    'Luis Rodríguez',
    'Sofia García',
    'Miguel Fernández',
    'Laura Sánchez',
]

def generate_random_reviews():
    """Generate a random number of reviews with random Lorem ipsum text"""
    num_reviews = random.randint(1, 5)
    reviews = []
    
    for i in range(num_reviews):
        # Generate random text length between 50 and 250
        text_length = random.randint(50, 250)
        
        # Clean the lorem ipsum text and create a pool
        clean_text = LOREM_IPSUM.replace('\n', ' ').split()
        
        # Generate review text by randomly selecting words
        review_text = ''
        while len(review_text) < text_length:
            word = random.choice(clean_text)
            review_text += word + ' '
        
        # Trim to exact length requirements
        review_text = review_text.strip()
        if len(review_text) > 250:
            review_text = review_text[:250].rsplit(' ', 1)[0] + '.'
        
        review = {
            'name': random.choice(REVIEWER_NAMES),
            'avatar': random.choice(AVATARS),
            'text': review_text,
            'date': f'{random.randint(1, 28)}.{random.randint(1, 12)}.{random.randint(2020, 2024)}'
        }
        reviews.append(review)
    
    return reviews

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories,
            is_available=True
        ).order_by('id')
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(
            is_available=True
        ).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug,
            slug=product_slug
        )
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e
    
    # Generate random reviews
    reviews = generate_random_reviews()
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)