from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from products.models import Product, Category, Brand, SubCategory
from banners.models import Banner
from orders.models import Order, Coupon   , Offer
from accounts.models import Customer, Governorate, City
from contact.models import ContactMessage
from wishlist.models import Wishlist
from django.db.models import Sum, Count, Q
from .forms import (
    ProductForm, OrderStatusForm, CustomerForm, ProductImageFormSet,
    CategoryForm, SubCategoryForm, BrandForm, BannerForm,
    GovernorateForm, CityForm, CouponForm
)

class DashboardLoginView(LoginView):
    template_name = 'backend/login.html'
    
    def get_success_url(self):
        return '/manage-perfumes/'

def dashboard_access_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('backend:login')
        if request.user.role in ['admin', 'manager', 'supervisor', 'employee']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

# ── Coupons ──────────────────────────────────────────────────────

@dashboard_access_required
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'backend/coupons.html', {'coupons': coupons})

@dashboard_access_required
def coupon_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(Coupon, pk=pk) if pk else None
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:coupon_list')
    else:
        form = CouponForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة الكوبونات'})

# ── Contact Messages ─────────────────────────────────────────────

@dashboard_access_required
def message_list(request):
    messages = ContactMessage.objects.all()
    return render(request, 'backend/messages.html', {'messages': messages})

@dashboard_access_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'backend/message_detail.html', {'message': msg})

# ── Wishlists ────────────────────────────────────────────────────

@dashboard_access_required
def wishlist_list(request):
    wishlists = Wishlist.objects.all().order_by('-created_at')
    return render(request, 'backend/wishlists.html', {'wishlists': wishlists})

@dashboard_access_required
def wishlist_detail(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk)
    return render(request, 'backend/wishlist_detail.html', {'wishlist': wishlist})

# ── Governorates & Cities ────────────────────────────────────────

@dashboard_access_required
def governorate_list(request):
    governorates = Governorate.objects.all().order_by('name_ar')
    return render(request, 'backend/governorates.html', {'governorates': governorates})

@dashboard_access_required
def governorate_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(Governorate, pk=pk) if pk else None
    if request.method == 'POST':
        form = GovernorateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:governorate_list')
    else:
        form = GovernorateForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة المحافظات'})

@dashboard_access_required
def city_list(request):
    cities = City.objects.all().order_by('governorate', 'name_ar')
    return render(request, 'backend/cities.html', {'cities': cities})

@dashboard_access_required
def city_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(City, pk=pk) if pk else None
    if request.method == 'POST':
        form = CityForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:city_list')
    else:
        form = CityForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة المدن'})

# ── Banners ──────────────────────────────────────────────────────

@dashboard_access_required
def banner_list(request):
    banners = Banner.objects.all().order_by('position', 'order')
    return render(request, 'backend/banners.html', {'banners': banners})

@dashboard_access_required
def banner_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(Banner, pk=pk) if pk else None
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:banner_list')
    else:
        form = BannerForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة البنرات'})

# ── Categories ───────────────────────────────────────────────────

@dashboard_access_required
def category_list(request):
    categories = Category.objects.all().order_by('name_ar')
    return render(request, 'backend/categories.html', {'categories': categories})

@dashboard_access_required
def category_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(Category, pk=pk) if pk else None
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:category_list')
    else:
        form = CategoryForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة الفئات'})

@dashboard_access_required
def category_delete(request, pk):
    if not request.user.can_delete_data: raise PermissionDenied
    get_object_or_404(Category, pk=pk).delete()
    return redirect('backend:category_list')

# ── SubCategories ───────────────────────────────────────────────

@dashboard_access_required
def subcategory_list(request):
    subcategories = SubCategory.objects.all().order_by('category', 'name_ar')
    return render(request, 'backend/subcategories.html', {'subcategories': subcategories})

@dashboard_access_required
def subcategory_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(SubCategory, pk=pk) if pk else None
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:subcategory_list')
    else:
        form = SubCategoryForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة الفئات الفرعية'})

# ── Brands ───────────────────────────────────────────────────────

@dashboard_access_required
def brand_list(request):
    brands = Brand.objects.all().order_by('name')
    return render(request, 'backend/brands.html', {'brands': brands})

@dashboard_access_required
def brand_upsert(request, pk=None):
    if not request.user.can_manage_products: raise PermissionDenied
    instance = get_object_or_404(Brand, pk=pk) if pk else None
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:brand_list')
    else:
        form = BrandForm(instance=instance)
    return render(request, 'backend/generic_form.html', {'form': form, 'title': 'إدارة العلامات التجارية'})

@dashboard_access_required
def index(request):
    # إحصائيات للمدراء والمشرفين
    is_admin = request.user.role.lower() in ['admin', 'manager', 'supervisor']
    
    total_sales = 0
    total_orders = 0
    total_customers = 0
    top_products_count = 0
    
    if is_admin:
        total_sales = Order.objects.filter(status='delivered').aggregate(Sum('total'))['total__sum'] or 0
        total_orders = Order.objects.count()
        total_customers = Customer.objects.filter(role__iexact='customer').count()
        # حساب المنتجات الأكثر مبيعاً (منتجات فريدة تم طلبها في طلبات ناجحة)
        top_products_count = Product.objects.filter(order_items__order__status='delivered').distinct().count()
    
    # الطلبات التي تحتاج إجراء (pending or processing)
    pending_orders = Order.objects.filter(status__in=['pending', 'processing']).order_by('-created_at')[:10]
    # آخر 10 رسائل
    latest_messages = ContactMessage.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'top_products_count': top_products_count,
        'pending_orders': pending_orders,
        'latest_messages': latest_messages,
        'is_admin': is_admin,
    }
    return render(request, 'backend/index.html', context)

@dashboard_access_required
def product_list(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'backend/products.html', context)

@dashboard_access_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # الفلاتر
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    payment = request.GET.get('payment', '')
    
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) | 
            Q(customer__first_name__icontains=q) | 
            Q(customer__last_name__icontains=q) |
            Q(shipping_phone__icontains=q)
        )
    
    if status:
        orders = orders.filter(status=status)
        
    if payment:
        orders = orders.filter(payment_method=payment)
        
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
        
    context = {
        'orders': orders,
        'status_choices': Order.Status.choices,
        'payment_choices': Order.PaymentMethod.choices,
        'filters': {
            'q': q,
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'payment': payment,
        }
    }
    return render(request, 'backend/orders.html', context)

@dashboard_access_required
def customer_list(request):
    customers = Customer.objects.filter(role='customer').order_by('-created_at')
    
    # البحث
    q = request.GET.get('q', '')
    if q:
        customers = customers.filter(
            Q(first_name__icontains=q) | 
            Q(last_name__icontains=q) | 
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    # إحصائيات حقيقية
    total_customers_count = Customer.objects.filter(role='customer').count()
    active_today_count = Customer.objects.filter(
        role='customer', 
        last_login__date=timezone.now().date()
    ).count()
    
    # إضافة بيانات الطلبات لكل عميل
    customers = customers.annotate(
        total_orders_count=Count('orders'),
        total_spent=Sum('orders__total', filter=Q(orders__status='delivered'))
    )
    
    context = {
        'customers': customers,
        'total_customers_count': total_customers_count,
        'active_today_count': active_today_count,
        'q': q
    }
    return render(request, 'backend/customers.html', context)

@dashboard_access_required
def staff_list(request):
    if request.user.role != 'admin':
        raise PermissionDenied

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        email      = request.POST.get('email')
        password   = request.POST.get('password')
        role       = request.POST.get('role')

        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم بالفعل.')
        else:
            Customer.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role
            )
            messages.success(request, f'تم إضافة الموظف {first_name} {last_name} بنجاح.')
            return redirect('staff_list')

    staff = Customer.objects.exclude(role='customer').order_by('role')
    context = {
        'staff': staff,
        'roles': Customer.ROLE_CHOICES
    }
    return render(request, 'backend/staff.html', context)


@dashboard_access_required
def edit_staff(request, pk):
    if request.user.role != 'admin':
        raise PermissionDenied
    member = Customer.objects.get(pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(Customer.ROLE_CHOICES):
            member.role = new_role
            member.save()
            return redirect('backend:staff_list')
    return redirect('backend:staff_list')

# CRUD Views

@dashboard_access_required
def product_create(request):
    if not request.user.can_manage_products:
        raise PermissionDenied
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            if '_continue' in request.POST:
                return redirect('backend:product_edit', pk=product.pk)
            return redirect('backend:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    return render(request, 'backend/product_form.html', {
        'form': form, 
        'formset': formset,
        'title': 'إضافة منتج جديد'
    })

@dashboard_access_required
def product_edit(request, pk):
    if not request.user.can_manage_products:
        raise PermissionDenied
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            if '_continue' in request.POST:
                return redirect('backend:product_edit', pk=product.pk)
            return redirect('backend:product_list')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    return render(request, 'backend/product_form.html', {
        'form': form, 
        'formset': formset,
        'title': 'تعديل المنتج', 
        'product': product
    })

@dashboard_access_required
def product_delete(request, pk):
    if not request.user.can_delete_data:
        raise PermissionDenied
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('backend:product_list')

import urllib.parse

@dashboard_access_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    whatsapp_url = None
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            # تجهيز رسالة واتساب
            if order.customer and order.customer.has_whatsapp:
                status_text = order.get_status_display()
                message = f"أهلاً {order.customer.first_name}، تم تحديث حالة طلبك رقم #{order.order_number} إلى: {status_text}. شكراً لتسوقك معنا!"
                phone = order.customer.phone or order.shipping_phone
                if phone:
                    clean_phone = "".join(filter(str.isdigit, phone))
                    if not (clean_phone.startswith('2') or clean_phone.startswith('00')):
                        clean_phone = '20' + clean_phone # Egypt default
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(message)}"
            
            if not whatsapp_url:
                return redirect('backend:order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)
    
    return render(request, 'backend/order_detail.html', {
        'order': order, 
        'form': form,
        'whatsapp_url': whatsapp_url
    })

@dashboard_access_required
def customer_edit(request, pk):
    if not request.user.is_manager:
        raise PermissionDenied
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('backend:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'backend/customer_form.html', {'customer': customer, 'form': form})


# ── Offers ───────────────────────────────────────────────────────

@dashboard_access_required
def offer_list(request):
    offers = Offer.objects.all().order_by('-created_at')
    return render(request, 'backend/offers.html', {'offers': offers})


@dashboard_access_required
def offer_upsert(request, pk=None):
    if not request.user.can_manage_products:
        raise PermissionDenied
    from .forms import OfferForm
    instance = get_object_or_404(Offer, pk=pk) if pk else None
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('backend:offer_list')
    else:
        form = OfferForm(instance=instance)
    return render(request, 'backend/offer_form.html', {
        'form':  form,
        'title': 'إضافة عرض' if not instance else 'تعديل العرض',
    })


@dashboard_access_required
def offer_delete(request, pk):
    if not request.user.can_delete_data:
        raise PermissionDenied
    get_object_or_404(Offer, pk=pk).delete()
    return redirect('backend:offer_list')