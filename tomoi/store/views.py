from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import (
    Order, PurchasedAccount, Product, ProductImage, 
    Category, Banner, CartItem, BlogPost, ProductVariant, 
    VariantOption
)
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
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
import time
from decimal import Decimal


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
    
    context = {
        'product': product,
        'related_products': Product.objects.filter(category=product.category).exclude(id=product.id)[:4],
        'cross_sale_products': product.cross_sale_products.all(),
        'blog_posts': BlogPost.objects.filter(products=product),
    }
    
    return render(request, 'store/product_detail.html', context)

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
    return render(request, 'store/payment_success.html')

def payment_failed(request):
    return render(request, 'store/payment_failed.html')

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
    # Lấy cart items trực tiếp từ CartItem
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Tính toán các giá trị
    total_amount = sum(item.total_price() for item in cart_items)
    discount_amount = 0  # Tính giảm giá nếu có
    final_amount = total_amount - discount_amount
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
    }
    
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        duration = data.get('duration')
        upgrade_email = data.get('upgrade_email')
        account_username = data.get('account_username')
        account_password = data.get('account_password')
        quantity = data.get('quantity', 1)

        # Kiểm tra xác thực
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng'
            }, status=401)

        # Lấy thông tin sản phẩm
        product = get_object_or_404(Product, id=product_id)
        
        # Kiểm tra các trường bắt buộc
        if product.requires_email and not upgrade_email:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng nhập email cần nâng cấp'
            })
            
        if product.requires_account_password and (not account_username or not account_password):
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng nhập đầy đủ thông tin tài khoản cần nâng cấp'
            })

        # Tạo hoặc cập nhật cart item
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            variant_id=variant_id,
            duration=duration,
            upgrade_email=upgrade_email,
            account_username=account_username,
            account_password=account_password,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Lấy thông tin giỏ hàng mới
        cart_items = get_cart_items(request)
        total_items = sum(item['quantity'] for item in cart_items)

        return JsonResponse({
            'success': True,
            'cart_items': cart_items,
            'total_items': total_items
        })

    except Exception as e:
        print(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Update context in view
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['cart_items'] = self.request.session.get('cart_items', [])
    return context

@require_POST
def get_cart_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'cart_items': [],
            'total_items': 0
        })
    
    try:
        user = request.user
        session_key = request.session.session_key

        cart_items = CartItem.objects.filter(
            Q(user=user) | Q(session_key=session_key)
        ).select_related('product')

        items = [{
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'price': float(item.total_price()),
            'quantity': item.quantity,
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'stock': item.product.stock,
            'variant_name': item.variant.name if item.variant else None,
            'duration': item.duration
        } for item in cart_items]

        return JsonResponse({
            'cart_items': items,
            'total_items': sum(item['quantity'] for item in items)
        })
    except Exception as e:
        print("Cart API error:", str(e))
        return JsonResponse({
            'cart_items': [],
            'total_items': 0
        })

# Xóa sản phẩm khỏi giỏ
@require_POST
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        cart_item = CartItem.objects.get(id=data['id'])
        cart_item.delete()
        
        # Tính toán lại tổng
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart_items = CartItem.objects.filter(session_key=request.session.session_key)
            
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.total_price() for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'total_items': total_items,
            'total_amount': total_amount
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

@require_http_methods(["GET"])
def cart_api(request):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart_items = CartItem.objects.filter(session_key=request.session.session_key)

        items = [{
            'id': item.id,  # ID của CartItem, không phải Product ID
            'product_id': item.product.id,
            'name': item.product.name,
            'price': float(item.total_price()),
            'quantity': item.quantity,
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'stock': item.product.stock,
            'variant_name': item.variant.name if item.variant else None,
            'duration': item.duration
        } for item in cart_items]

        return JsonResponse({
            'cart_items': items,
            'total_items': sum(item['quantity'] for item in items)
        })
    except Exception as e:
        return JsonResponse({
            'cart_items': [],
            'total_items': 0
        })

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

@login_required
def update_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId')
        quantity = data.get('quantity')
        
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        
        # Lấy danh sách cart items đã cập nhật
        cart_items = CartItem.objects.filter(user=request.user)
        
        # Tính tổng tiền
        total_amount = sum(item.total_price() for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'cart_items': [item.to_dict() for item in cart_items],
            'total_items': sum(item.quantity for item in cart_items),
            'total_amount': total_amount
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sản phẩm không tồn tại trong giỏ hàng'
        })
    except Exception as e:
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
        product = Product.objects.get(id=product_id)
        return JsonResponse({'stock': product.stock})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def format_price(value):
    """Format giá tiền theo định dạng Việt Nam"""
    try:
        return f"{int(value):,}đ".replace(',', '.')
    except (ValueError, TypeError):
        return value

@require_http_methods(["GET"])
def get_variant_price(request):
    variant_id = request.GET.get('variant_id')
    duration = request.GET.get('duration')
    
    try:
        variant = ProductVariant.objects.get(id=variant_id)
        option = variant.options.get(duration=duration)
        
        return JsonResponse({
            'success': True,
            'price': option.price,
            'old_price': variant.product.old_price if variant.product.old_price else None,
            'discount': variant.product.get_discount_percentage()
        })
    except (ProductVariant.DoesNotExist, VariantOption.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy thông tin giá'
        })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_active=True)
    related_products = post.products.all()
    
    return render(request, 'store/blog_detail.html', {
        'post': post,
        'related_products': related_products
    })

def get_cart_items(request):
    # Nếu không đăng nhập, trả về list rỗng
    if not request.user.is_authenticated:
        return []
        
    # Nếu đã đăng nhập, lấy cart items của user
    cart_items = CartItem.objects.filter(user=request.user)
    
    return [{
        'id': item.id,
        'name': item.product.name,
        'price': float(item.total_price()),
        'quantity': item.quantity,
        'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
        'stock': item.product.stock,
        'variant_name': item.variant.name if item.variant else None,
        'duration': item.duration,
        'upgrade_email': item.upgrade_email,
        'account_username': item.account_username
    } for item in cart_items]
