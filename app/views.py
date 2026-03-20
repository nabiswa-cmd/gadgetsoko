from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from .models import Product, Category, ProductImage, CartItem, Order, OrderItem

import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth
import json


# ================= HOME =================
def index_view(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


# ================= PRODUCTS =================
def products_view(request):
    category_id = request.GET.get('category')

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()

    return render(request, 'products.html', {
        'products': products,
        'categories': categories
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def view_cart(request):
    items = request.user.cart_items.all()

    total = sum(item.product.discounted_price * item.quantity for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })

from .models import Category

def create_default_categories():
    categories = [
        "Kitchen Appliances",
        "Phones & Tablets",
        "Computers & Laptops",
        "TVs & Entertainment",
        "Audio Devices",
        "Networking Equipment",
        "Home Appliances",
        "Power & Electrical Accessories",
        "Cables & Connectors",
        "Batteries & Power Banks",
        "Lighting Equipment",
        "CCTV & Security Systems",
        "Gaming Accessories",
        "Smart Home Devices",
        "Wearables",
        "Office Electronics",
        "Printers & Scanners",
        "Computer Accessories",
        "Mobile Accessories",
        "Solar & Energy Solutions",
        "Extension Cables & Adaptors",
        "Chargers & Adapters",
        "Fans & Cooling Systems",
        "Irons & Heating Appliances",
        "Fridges & Freezers",
        "Cookers & Ovens",
        "Blenders & Mixers",
        "Microwaves",
        "Electric Kettles"
    ]

    for cat in categories:
        Category.objects.get_or_create(name=cat)


    
@staff_member_required
def customers(request):
    orders = Order.objects.select_related('user').prefetch_related('orderitem_set').order_by('-created_at')

    return render(request, 'customers.html', {
        'orders': orders
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.views += 1
    product.save()

    return render(request, 'product_detail.html', {'product': product})

def products_by_brand(request, brand_name):
    products = Product.objects.filter(brand__name=brand_name)
    return render(request, 'products_by_brand.html', {
        'products': products,
        'brand': brand_name
    })
# ================= CART =================
from .models import Brand

@login_required
def add_product(request):
    create_default_categories()
    categories = Category.objects.all()
    brands = Brand.objects.all()  # ✅ ADD THIS

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        discount = request.POST.get("discount")
        stock = request.POST.get("stock")
        brand_id = request.POST.get("brand")
        category_id = request.POST.get("category")
        new_category = request.POST.get("new_category")
        specifications = request.POST.get("specifications")

        if new_category:
            category = Category.objects.create(name=new_category)
        else:
            category = Category.objects.get(id=category_id)

        brand = Brand.objects.get(id=brand_id)  # ✅ FIX HERE

        Product.objects.create(
            name=name,
            price=price,
            discount=discount,
            stock=stock,
            category=category,
            brand=brand,
            specifications=specifications
        )

        return redirect("products")  # optional but good

    return render(request, "add_product.html", {
        "categories": categories,
        "brands": brands  # ✅ CRITICAL
    })
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.quantity * item.product.price for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('view_cart')



# ================= CHECKOUT =================
@login_required
def check(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.quantity * item.product.price for item in cart_items)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            destination=address,
            total=total,
            status="Pending",
            payment_status="Pending"
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        response = lipa_na_mpesa(
            phone_number=phone,
            amount=total,
            account_ref=f"ORDER{order.id}",
            transaction_desc="Gadget Purchase"
        )

        print("STK RESPONSE:", response)

        return HttpResponse("Check your phone to complete payment.")

    return render(request, 'check.html', {'total': total})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')
# ================= AUTH =================
def signup_view(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )
        return redirect('login')

    return render(request, 'signup.html')

from django.http import JsonResponse
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth


def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        )
    )

    return response.json().get('access_token')


def usersignup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username exists")
            else:
                User.objects.create_user(username=username, email=email, password=password1)
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'usersignup.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('dashboard' if user.is_staff else 'index')

        messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


def userlog_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'userlog.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ================= DASHBOARD =================
@staff_member_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {
        'products': Product.objects.count(),
        'orders': Order.objects.count(),
        'users': User.objects.count(),
        'revenue': sum(order.total for order in Order.objects.all()),
    })


# ================= PRODUCT MANAGEMENT =================
@staff_member_required
def manage_products(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'manage_products.html', {'products': products})


@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_products')


# ================= ORDERS =================
@staff_member_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-id')
    return render(request, 'manage_orders.html', {'orders': orders})


@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = request.POST.get('status')
    order.save()
    return redirect('manage_orders')


# ================= MPESA =================


def lipa_na_mpesa(phone_number, amount, account_ref, transaction_desc):
    token = get_mpesa_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode("utf-8")

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": transaction_desc
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("MPESA RESPONSE:", response.text)

    return response.json()


# ================= CALLBACK =================
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    print("MPESA CALLBACK:", data)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
def register_mpesa_urls(request):
    access_token = get_mpesa_access_token()

    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "ShortCode": settings.MPESA_SHORTCODE,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://eloy-headstrong-eventfully.ngrok-free.dev/payment_callback/",
        "ValidationURL": "https://eloy-headstrong-eventfully.ngrok-free.dev/payment_callback/",
    }

    response = requests.post(api_url, json=payload, headers=headers)

    return JsonResponse(response.json())

    
    response = requests.post(api_url, json=payload, headers=headers)

    return JsonResponse(response.json())