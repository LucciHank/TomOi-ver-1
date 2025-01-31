from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Order, PurchasedAccount, Product, ProductImage, Category, Banner, CartItem  # Tạm thời bỏ CartItem
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .utils import send_payment_confirmation_email
from django.contrib import messages
import json
from django.http import JsonResponse
from django.utils.timezone import now, timedelta, datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ProductImageForm
from django.contrib.auth import logout, login, authenticate
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.db.models import Q
# from paypalrestsdk import Payment
# import paypalrestsdk


def dashboard(request):
    return render(request, 'store/index.html')

def home(request):
    context = {
        'main_banners': Banner.objects.filter(location='main', is_active=True),
        'side1_banners': Banner.objects.filter(location='side1', is_active=True),
        'side2_banners': Banner.objects.filter(location='side2', is_active=True),
        'left_banners': Banner.objects.filter(location='left', is_active=True),
        'right_banners': Banner.objects.filter(location='right', is_active=True),
        'categories': Category.objects.all(),
        'products': Product.objects.filter(is_featured=True),
    }
    return render(request, 'store/home.html', context)

def add_images_to_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Lặp qua tất cả các hình ảnh được tải lên
        for image_file in request.FILES.getlist('image'):
            is_primary = 'is_primary' in request.POST and image_file.name == request.POST.get('primary_image')
            ProductImage.objects.create(product=product, image=image_file, is_primary=is_primary)

        return redirect('store:product_detail', product_id=product.id)

    else:
        # Nếu không phải POST, chỉ render form
        form = ProductImageForm()

    return render(request, 'store/add_images', {'form': form, 'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()
    return render(request, 'store/product_detail', {'product': product, 'variants': variants})

@login_required
def add_balance(request, amount):
    request.user.balance += amount  # Cộng tiền vào tài khoản
    request.user.save()
    messages.success(request, f"Bạn đã nhận được {amount} VNĐ vào tài khoản!")
    return redirect("profile")  # Chuyển hướng về trang cá nhân

@login_required
def user_profile(request):
    return render(request, 'store/profile.html', {
        'user': request.user
    })

def user_info(request):
    return render(request, 'store/user_info.html')

def recharge(request):
    return render(request, 'store/recharge.html')

@login_required
def buy_premium_account(request, account_type, price, duration_days):
    if request.user.balance < price:
        messages.error(request, "Bạn không đủ tiền trong tài khoản!")
        return redirect("store")

    request.user.balance -= price  # Trừ tiền
    request.user.save()

    expiry_date = now().date() + timedelta(days=duration_days)  # Tính hạn premium
    PurchasedAccount.objects.create(user=request.user, account_type=account_type, expiry_date=expiry_date)

    messages.success(request, f"Bạn đã mua thành công {account_type}. Hạn sử dụng đến {expiry_date}")
    return redirect("purchased_accounts")

@login_required
def purchased_accounts(request):
    accounts = PurchasedAccount.objects.filter(user=request.user)
    return render(request, 'store/purchased_accounts.html', {'accounts': accounts})

def product_list(request):
    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {'categories': categories})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def payment_success(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    if not payment_id or not payer_id:
        messages.error(request, "Lỗi thanh toán: Không tìm thấy thông tin giao dịch.")
        return redirect("store:checkout")

    # # Lấy Payment từ PayPal SDK
    # payment = Payment.find(payment_id)

    # if payment.execute({"payer_id": payer_id}):  # Xác nhận thanh toán
    #     order = Order.objects.get(user=request.user, payment_id=payment_id)
    #     order.status = "PAID"
    #     order.save()

        # Gửi email xác nhận
        send_payment_confirmation_email(request.user, order)

        messages.success(request, "Thanh toán thành công! Kiểm tra email để nhận thông tin đơn hàng.")
        return redirect("store:order_history")
    else:
        messages.error(request, "Thanh toán không thành công. Vui lòng thử lại.")
        return redirect("store:checkout")

def send_payment_confirmation_email(user, order):
    subject = "Xác nhận thanh toán thành công"
    message = f"Chào {user.username},\n\nĐơn hàng #{order.id} của bạn đã được thanh toán thành công."
    send_mail(subject, message, 'hoanganhdo181@gmail.com', [user.email])

#cart
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def cart_view(request):
    # Lấy user hoặc session key
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key if not user else None

    # Lấy cart items từ database
    cart_items = CartItem.objects.filter(
        Q(user=user) | Q(session_key=session_key)
    ).select_related('product')  # Tối ưu query bằng select_related

    # Tính tổng tiền
    total_price = sum(item.total_price() for item in cart_items)

    context = {
        'cart_items': [{
            'id': item.id,
            'product': item.product,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'total': item.total_price(),
            'image': item.product.get_primary_image() if hasattr(item.product, 'get_primary_image') else None
        } for item in cart_items],
        'total_price': total_price
    }

    return render(request, 'store/cart.html', context)

@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing product ID'
            })

        product = get_object_or_404(Product, id=product_id)
        
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        cart_item = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key),
            product=product
        ).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                user=user,
                session_key=session_key,
                product=product,
                quantity=quantity
            )

        cart_items = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key)
        ).select_related('product')
        
        items = [{
            'id': item.product.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'old_price': str(item.product.old_price) if item.product.old_price else None,
            'discount': item.product.get_discount_percentage(),
            'quantity': item.quantity,
            'total': str(item.total_price()),
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'stock': item.product.stock
        } for item in cart_items]

        return JsonResponse({
            'success': True,
            'cart_items': items
        })
        
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Update context in view
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['cart_items'] = self.request.session.get('cart_items', [])
    return context

@login_required
def get_cart_api(request):
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key

    cart_items = CartItem.objects.filter(
        Q(user=user) | Q(session_key=session_key)
    ).select_related('product')

    items = [{
        'id': item.product.id,
        'name': item.product.name,
        'price': str(item.product.price),
        'old_price': str(item.product.old_price) if item.product.old_price else None,
        'discount': item.product.get_discount_percentage(),
        'quantity': item.quantity,
        'total': str(item.total_price()),
        'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
        'stock': item.product.stock
    } for item in cart_items]

    return JsonResponse({
        'cart_items': items,
        'total_items': sum(item.quantity for item in cart_items)
    })

# Xóa sản phẩm khỏi giỏ
@require_http_methods(["POST"])
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('id')
        
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key),
            product_id=product_id
        ).delete()

        cart_items = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key)
        ).select_related('product')

        items = [{
            'id': item.product.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'old_price': str(item.product.old_price) if item.product.old_price else None,
            'discount': item.product.get_discount_percentage(),
            'quantity': item.quantity,
            'total': str(item.total_price()),
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'stock': item.product.stock
        } for item in cart_items]

        return JsonResponse({
            'success': True,
            'cart_items': items
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Xóa toàn bộ giỏ hàng
def clear_cart(request):
    request.session['cart_items'] = []
    return redirect('store:cart')

# Thanh toán
@login_required
def checkout(request):
    if request.method == 'POST':
        cart_items = request.session.get('cart_items', [])

        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Giỏ hàng trống.'})

        # Tính tổng tiền từ giỏ hàng
        total_amount = sum(item['quantity'] * item['price'] for item in cart_items)

        try:
            # Tạo đơn hàng mới
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,  # Gán giá trị total_amount
            )

            # Lưu từng sản phẩm vào chi tiết đơn hàng
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price'],
                )

                # Cập nhật kho
                product.stock -= item['quantity']
                product.save()

            # Dọn sạch giỏ hàng
            request.session['cart_items'] = []

            return JsonResponse({'success': True, 'message': 'Đặt hàng thành công.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Có lỗi xảy ra.', 'error': str(e)})

@login_required
def cart_api(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'cart': list(cart.values()), 'total_items': total_items})

def paypal_webhook(request):
    data = json.loads(request.body)
    if data['event_type'] == 'PAYMENT.SALE.COMPLETED':
        payment_id = data['resource']['parent_payment']
        order = Order.objects.filter(paypal_payment_id=payment_id).first()
        if order:
            order.status = "Completed"
            order.save()
    return JsonResponse({"status": "ok"})
# paypalrestsdk.configure({
#     'mode': settings.PAYPAL_MODE,
#     'client_id': settings.PAYPAL_CLIENT_ID,
#     'client_secret': settings.PAYPAL_CLIENT_SECRET
# })

# def paypal_payment(request):
#     payment = paypalrestsdk.Payment({
#         "intent": "sale",
#         "payer": {
#             "payment_method": "paypal"
#         },
#         "redirect_urls": {
#             "return_url": "http://localhost:8000/payment/execute/",
#             "cancel_url": "http://localhost:8000/payment/cancel/"
#         },
#         "transactions": [{
#             "amount": {
#                 "total": "10.00",
#                 "currency": "USD"
#             },
#             "description": "Thanh toán tài khoản premium"
#         }]
#     })

#     if payment.create():
#         for link in payment.links:
#             if link.rel == "approval_url":
#                 approval_url = link.href
#                 return redirect(approval_url)
#     return redirect('payment_error')

# def payment_execute(request):
#     payment = paypalrestsdk.Payment.find(request.GET['paymentId'])
#     if payment.execute({"payer_id": request.GET["PayerID"]}):
#         return render(request, 'payment_success.html')
#     return render(request, 'payment_error.html')

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'store/category_detail.html', context)

@require_http_methods(["POST"])
def update_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('id')
        quantity = data.get('quantity', 1)
        
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        cart_item = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key),
            product_id=product_id
        ).first()

        if cart_item:
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()

        cart_items = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key)
        ).select_related('product')

        items = [{
            'id': item.product.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'old_price': str(item.product.old_price) if item.product.old_price else None,
            'discount': item.product.get_discount_percentage(),
            'quantity': item.quantity,
            'total': str(item.total_price()),
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'stock': item.product.stock
        } for item in cart_items]

        return JsonResponse({
            'success': True,
            'cart_items': items
        })

    except Exception as e:
        print("Error updating cart:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def get_cart_count(request):
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key

    cart_items = CartItem.objects.filter(
        Q(user=user) | Q(session_key=session_key)
    )
    
    return JsonResponse({
        'count': sum(item.quantity for item in cart_items)
    })

def check_stock(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        return JsonResponse({
            'success': True,
            'stock': product.stock,
            'product_id': product.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)