from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import AccountAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=AccountAuthenticationForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/password/', views.password_change, name='password_change'),
    path('orders/<int:order_pk>/', views.user_order_detail, name='user_order_detail'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:pk>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:pk>/orders/<int:order_pk>/', views.admin_user_order_detail, name='admin_user_order_detail'),
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/new/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/<int:pk>/', views.admin_product_detail, name='admin_product_detail'),
    path('admin/products/<int:pk>/edit/', views.admin_product_edit, name='admin_product_edit'),
]
