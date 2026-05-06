from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm
from django.http import JsonResponse
from .models import City


def merge_guest_data_to_account(request, user):
    """
    نقل بيانات السلة والمفضلة من السيشن (للضيف) إلى قاعدة البيانات (للحساب المسجل)
    """
    # ── دمج السلة ────────────────────────────────────────────────
    session_cart = request.session.get('cart', {})
    if session_cart:
        from orders.models import Cart, CartItem
        cart, _ = Cart.objects.get_or_create(customer=user)
        for p_id, qty in session_cart.items():
            item, created = CartItem.objects.get_or_create(
                cart=cart, product_id=p_id,
                defaults={'quantity': qty}
            )
            if not created:
                item.quantity += qty
                item.save()
        del request.session['cart']

    # ── دمج المفضلة ──────────────────────────────────────────────
    session_wishlist = request.session.get('wishlist', [])
    if session_wishlist:
        from wishlist.models import Wishlist, WishlistItem
        wishlist, _ = Wishlist.objects.get_or_create(customer=user)
        for p_id in session_wishlist:
            WishlistItem.objects.get_or_create(wishlist=wishlist, product_id=p_id)
        del request.session['wishlist']
    
    request.session.modified = True


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
        
    next_url = request.GET.get('next', 'home')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                merge_guest_data_to_account(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
        
    next_url = request.GET.get('next', 'home')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            merge_guest_data_to_account(request, user)
            messages.success(request, "Registration successful!")
            return redirect(next_url)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")


def get_cities(request):
    governorate_id = request.GET.get("governorate_id")
    if not governorate_id:
        return JsonResponse({"cities": []})
    
    cities = City.objects.filter(
        governorate_id=governorate_id,
        is_active=True
    ).values("id", "name_ar", "name_en", "shipping_cost")
    
    return JsonResponse({"cities": list(cities)})
