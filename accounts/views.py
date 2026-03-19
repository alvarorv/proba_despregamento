from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import Order
from store.forms import ProductForm
from store.models import Product
from .forms import RegisterForm, ProfileForm, AdminUserForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('accounts:profile')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=user)

    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'form': form, 'orders': orders})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    for field in form.fields.values():
        field.widget.attrs.setdefault('class', 'form-control')

    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def user_order_detail(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})


def is_admin_user(user):
    return user.is_authenticated and (getattr(user, 'is_superadmin', False) or getattr(user, 'is_admin', False) or getattr(user, 'is_staff', False))


@user_passes_test(is_admin_user)
def admin_user_list(request):
    User = get_user_model()
    users = User.objects.all().order_by('id')
    return render(request, 'accounts/admin_user_list.html', {'users': users})


@user_passes_test(is_admin_user)
def admin_user_detail(request, pk):
    User = get_user_model()
    u = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=u).order_by('-created_at')
    return render(request, 'accounts/admin_user_detail.html', {'user_obj': u, 'orders': orders})


@user_passes_test(is_admin_user)
def admin_user_edit(request, pk):
    User = get_user_model()
    u = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('accounts:admin_user_detail', pk=u.id)
    else:
        form = AdminUserForm(instance=u)

    return render(request, 'accounts/admin_user_edit.html', {'user_obj': u, 'form': form})


@user_passes_test(is_admin_user)
def admin_user_delete(request, pk):
    User = get_user_model()
    u = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        u.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('accounts:admin_user_list')

    return render(request, 'accounts/admin_user_delete.html', {'user_obj': u})


@user_passes_test(is_admin_user)
def admin_user_order_detail(request, pk, order_pk):
    User = get_user_model()
    u = get_object_or_404(User, pk=pk)
    order = get_object_or_404(Order, pk=order_pk, user=u)
    return render(request, 'accounts/admin_order_detail.html', {'user_obj': u, 'order': order})


@user_passes_test(is_admin_user)
def admin_product_list(request):
    products = Product.objects.select_related('category').order_by('id')
    return render(request, 'accounts/admin_product_list.html', {'products': products})


@user_passes_test(is_admin_user)
def admin_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'accounts/admin_product_detail.html', {'product': product})


@user_passes_test(is_admin_user)
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('accounts:admin_product_detail', pk=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'accounts/admin_product_edit.html', {'product': product, 'form': form})


@user_passes_test(is_admin_user)
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('accounts:admin_product_detail', pk=product.id)
    else:
        form = ProductForm()

    return render(request, 'accounts/admin_product_create.html', {'form': form})
