from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import (
    Order, OrderItem, PurchasedAccount, Product, ProductImage, 
    Category, Banner, CartItem, BlogPost, ProductVariant, 
    VariantOption, Wishlist, SearchHistory, Review
)
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .utils import send_payment_confirmation_email, get_client_ip
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
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Count
import time
from decimal import Decimal
from django.db import transaction
from accounts.vnpay import VNPay
from payment.models import Transaction
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
import pyotp
from django.templatetags.static import static
from dashboard.models.chatbot import ChatLog, ChatFeedback
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape
from django.utils import timezone
from django.utils.text import slugify
import uuid
import os
from dashboard.models.conversation import Conversation, Message, UserNotification
import requests
import hmac
import hashlib
import logging

# Cấu hình logger
logger = logging.getLogger(__name__)

def format_price(value):
    """Format giá tiền theo định dạng Việt Nam"""
    try:
        return f"{int(value):,}đ".replace(',', '.')
    except (ValueError, TypeError):
        return value

def dashboard(request):
    return render(request, 'store/index.html')

def home(request):
    context = {
        'main_banners': Banner.objects.filter(location='main', is_active=True),
        'side1_banners': Banner.objects.filter(location='side1', is_active=True),
        'side2_banners': Banner.objects.filter(location='side2', is_active=True),
        'left_banners': Banner.objects.filter(location='left', is_active=True),
        'right_banners': Banner.objects.filter(location='right', is_active=True),
        'categories': Category.objects.filter(parent=None).distinct(),
        'featured_products': Product.objects.filter(is_featured=True, is_active=True)[:8],
        'bestseller_products': Product.objects.filter(is_active=True).order_by('-sold_count')[:8],
        'new_products': Product.objects.filter(is_active=True).order_by('-created_at')[:8],
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
    """Chi tiết sản phẩm"""
    try:
        # Lấy sản phẩm theo ID
        product = get_object_or_404(Product, id=product_id)
        logger.info(f"Đang xem sản phẩm {product.name} (ID: {product.id})")
        
        # Khởi tạo các biến mặc định
        context = {
            'product': product,
            'is_in_wishlist': False
        }
        
        # Lấy danh sách sản phẩm yêu thích nếu user đã đăng nhập
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).exists()
            context['is_in_wishlist'] = wishlist_item
            logger.info(f"Sản phẩm trong wishlist: {wishlist_item}")
        
        # Lấy sản phẩm cross-sale
        cross_sale_products = []
        if product.cross_sale_products.exists():
            cross_sale_products = product.cross_sale_products.filter(is_active=True)
            context['cross_sale_products'] = cross_sale_products
            logger.info(f"Đã lấy {cross_sale_products.count()} sản phẩm cross-sale")
        
        return render(request, 'store/product_detail.html', context)
        
    except Exception as e:
        logger.error(f"Lỗi khi hiển thị chi tiết sản phẩm ID {product_id}: {str(e)}")
        messages.error(request, f"Có lỗi xảy ra khi tải thông tin sản phẩm: {str(e)}")
        return redirect('store:home')

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

@login_required
def recharge(request):
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
            payment_method = request.POST.get('payment_method')
            
            if amount < 10000:
                messages.error(request, 'Số tiền nạp tối thiểu là 10.000đ')
                return redirect('store:recharge')
            
            if payment_method == 'acb':
                transaction = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    payment_method='acb',
                    status='pending'
                )
                
                bank_info = {
                    'bank_name': 'Ngân hàng TMCP Á Châu (ACB)',
                    'account_number': '123456789',  # Thay bằng số tài khoản thật
                    'account_holder': 'NGUYEN VAN A',  # Thay bằng tên chủ tài khoản thật
                    'amount': amount,
                    'content': f'TOM{transaction.id}',
                    'transaction_id': transaction.id
                }
                
                return render(request, 'store/acb_transfer.html', {
                    'bank_info': bank_info
                })
            elif payment_method == 'vnpay':
                # Xử lý thanh toán VNPay
                pass
            elif payment_method == 'card':
                # Xử lý nạp thẻ cào
                pass
                
        except ValueError:
            messages.error(request, 'Số tiền không hợp lệ')
            return redirect('store:recharge')
            
    return render(request, 'store/recharge.html', {
        'username': request.user.username
    })

@login_required
def confirm_deposit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        
        if payment_method == 'acb':
            # Tạo giao dịch mới
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                payment_method='acb',
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Yêu cầu nạp tiền đã được gửi. Vui lòng chờ xác nhận.'
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Có lỗi xảy ra, vui lòng thử lại sau.'
    })

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
    """Hiển thị trang thanh toán thành công"""
    return render(request, 'store/payment_success.html')

def payment_failed(request):
    """Hiển thị trang thanh toán thất bại"""
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
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Tính tổng tiền giỏ hàng
    cart_total = sum(item.get_total_price() for item in cart_items)  # Đổi từ total_price() thành get_total_price()
    
    # Lấy các giảm giá từ session
    tcoin_discount = request.session.get('tcoin_discount', 0)
    voucher_discount = request.session.get('voucher_discount', 0)
    
    # Tính tổng số tiền cuối cùng
    final_amount = cart_total - tcoin_discount - voucher_discount
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'tcoin_discount': tcoin_discount,
        'voucher_discount': voucher_discount,
        'discount_amount': tcoin_discount + voucher_discount,
        'final_amount': final_amount,
    }
    
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        duration = data.get('duration')
        upgrade_email = data.get('upgrade_email')
        account_username = data.get('account_username')
        # Chỉ nhận account_password nhưng không lưu vào model
        account_password = data.get('account_password')

        # Kiểm tra sản phẩm tồn tại
        product = get_object_or_404(Product, id=product_id)
        
        # Lấy variant nếu có
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)

        # Tạo hoặc cập nhật cart item
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                variant=variant,
                duration=duration,
                upgrade_email=upgrade_email,
                defaults={
                    'quantity': quantity,
                    'account_username': account_username
                }
            )
        else:
            if not request.session.session_key:
                request.session.create()
            cart_item, created = CartItem.objects.get_or_create(
                session_key=request.session.session_key,
                product=product,
                variant=variant,
                duration=duration,
                upgrade_email=upgrade_email,
                defaults={
                    'quantity': quantity,
                    'account_username': account_username
                }
            )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        # Lấy thông tin giỏ hàng cập nhật để trả về cho client
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart_items = CartItem.objects.filter(session_key=request.session.session_key)
        
        # Tạo JSON cho cart items
        cart_items_json = [{
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'price': format_price(float(item.get_total_price())),
            'quantity': item.quantity,
            'image_url': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'variant_name': item.variant.name if item.variant else None,
            'duration': item.duration if item.duration else None
        } for item in cart_items]
        
        # Tính tổng số item trong giỏ
        total_items = sum(item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'message': 'Đã thêm vào giỏ hàng',
            'cart_items': cart_items_json,
            'total_items': total_items
        })

    except Exception as e:
        logger.error(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi thêm vào giỏ hàng',
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
        cart_items = CartItem.objects.filter(user=request.user)
        items_data = []
        
        for item in cart_items:
            items_data.append({
                'id': item.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'stock': item.product.stock,
                'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
                'variant_name': item.variant.name if hasattr(item, 'variant') and item.variant else None,
                'duration': item.duration if hasattr(item, 'duration') else None
            })
        
        return JsonResponse({
            'success': True,
            'cart_items': items_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

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
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).order_by('brand', 'duration')  # Sắp xếp theo brand và duration
    
    # Nhóm sản phẩm theo brand
    products_by_brand = {}
    for product in products:
        brand = product.get_brand_display()  # Lấy tên hiển thị của brand
        if brand not in products_by_brand:
            products_by_brand[brand] = []
        products_by_brand[brand].append(product)
    
    context = {
        'category': category,
        'products_by_brand': products_by_brand,
    }
    return render(request, 'store/category_detail.html', context)

@require_http_methods(["POST"])
def update_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))  # Convert to int with default 1
        action = data.get('action')

        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        product = cart_item.product

        # Kiểm tra stock
        if not product.stock:  # Nếu stock là None
            return JsonResponse({
                'success': False,
                'message': 'Sản phẩm đã hết hàng'
            })

        # Kiểm tra số lượng hợp lệ
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Chỉ còn {product.stock} sản phẩm trong kho'
            })

        if quantity < 1:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        # Lấy lại danh sách giỏ hàng mới
        cart_items = CartItem.objects.filter(user=request.user)
        items_data = [{
            'id': item.id,
            'name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'stock': item.product.stock or 0,  # Default 0 if None
            'image': item.product.get_primary_image().url if item.product.get_primary_image() else None,
            'total_price': float(item.get_total_price())
        } for item in cart_items]

        cart_total = sum(item.get_total_price() for item in cart_items)
        total_items = sum(item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'cart_items': items_data,
            'cart_total': cart_total,
            'total_items': total_items
        })

    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Sản phẩm không tồn tại trong giỏ hàng'
        })
    except Exception as e:
        print(f"Error updating cart: {str(e)}")  # Log lỗi
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi cập nhật giỏ hàng'
        }, status=400)

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

@login_required
@require_POST
def toggle_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            # Kiểm tra xem sản phẩm đã được yêu thích chưa
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
            
            if wishlist_item:
                # Nếu đã tồn tại, xóa khỏi danh sách yêu thích
                wishlist_item.delete()
                return JsonResponse({'status': 'removed', 'message': 'Đã xóa khỏi danh sách yêu thích'})
            else:
                # Nếu chưa tồn tại, thêm vào danh sách yêu thích
                Wishlist.objects.create(user=request.user, product=product)
                return JsonResponse({'status': 'added', 'message': 'Đã thêm vào danh sách yêu thích'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'}, status=405)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items
    }
    
    return render(request, 'store/wishlist.html', context)

@csrf_exempt 
def vnpay_order_return(request):
    """Xử lý kết quả trả về từ VNPay cho thanh toán đơn hàng"""
    if request.method == 'GET':
        vnpay = VNPay()
        vnpay.responseData = request.GET.dict()

        if vnpay.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            response_code = vnpay.responseData.get('vnp_ResponseCode')
            amount = Decimal(int(vnpay.responseData.get('vnp_Amount', 0)) / 100)
            order_id = vnpay.responseData.get('vnp_TxnRef')
            
            if response_code == '00':
                try:
                    with transaction.atomic():
                        # Cập nhật trạng thái đơn hàng
                        order = Order.objects.get(id=order_id)
                        order.status = 'paid'
                        order.save()
                        
                        # Lưu lịch sử giao dịch mua hàng
                        Transaction.objects.create(
                            user=request.user,
                            order=order,
                            amount=amount,
                            transaction_id=f"T{int(time.time())}", # T = Transaction
                            payment_method='vnpay',
                            status='success',
                            description='Thanh toán đơn hàng bằng VNPay'
                        )
                        
                        return render(request, 'accounts/success.html', {
                            'title': 'Thanh toán thành công!',
                            'message': f'Đơn hàng #{order.id} đã được thanh toán thành công'
                        })
                except Exception as e:
                    print(f"Error processing order: {str(e)}")
                    return render(request, 'accounts/success.html', {
                        'title': 'Lỗi!',
                        'message': 'Có lỗi xảy ra khi xử lý đơn hàng'
                    })
            else:
                return render(request, 'accounts/success.html', {
                    'title': 'Thất bại!', 
                    'message': 'Giao dịch thất bại hoặc bị hủy'
                })
        else:
            return render(request, 'accounts/success.html', {
                'title': 'Lỗi!',
                'message': 'Chữ ký không hợp lệ'
            })
    
    return redirect('store:cart')

def verify_2fa(user, auth_type, auth_value):
    """Xác thực 2FA"""
    if auth_type == 'password':
        return user.check_password(auth_value)
    elif auth_type == '2fa':
        if user.two_factor_method == 'password':
            return check_password(auth_value, user.two_factor_password)
        elif user.two_factor_method in ['email', 'google']:
            if user.two_factor_method == 'email':
                stored_otp = cache.get(f'email_otp_{user.id}')
                return stored_otp and stored_otp == auth_value
            elif user.two_factor_method == 'google':
                totp = pyotp.TOTP(user.google_auth_secret)
                return totp.verify(auth_value)
    return False

@login_required
@require_POST
def pay_with_balance(request):
    """Thanh toán đơn hàng bằng số dư"""
    try:
        data = json.loads(request.body)
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = Decimal(sum(item.quantity * item.product.price for item in cart_items))
        auth_type = data.get('auth_type')
        auth_value = data.get('auth_value')
        
        # Kiểm tra số dư
        if request.user.balance < cart_total:
            return JsonResponse({
                'success': False,
                'message': 'Số dư không đủ để thanh toán'
            })
            
        # Xác thực mật khẩu/2FA
        if auth_type == 'password':
            if not request.user.check_password(auth_value):
                return JsonResponse({
                    'success': False,
                    'message': 'Mật khẩu không chính xác'
                })
        elif auth_type == '2fa':
            if not verify_2fa(request.user, auth_type, auth_value):
                return JsonResponse({
                    'success': False,
                    'message': 'Mã xác thực không chính xác'
                })
                
        # Tạo đơn hàng
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=cart_total,
                payment_method='balance',
                status='paid'  # Đặt trạng thái là đã thanh toán
            )
            
            # Tạo chi tiết đơn hàng
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    variant=item.variant if hasattr(item, 'variant') else None,
                    duration=item.duration if hasattr(item, 'duration') else None,
                    upgrade_email=item.upgrade_email if hasattr(item, 'upgrade_email') else None
                )
            
            # Trừ số dư
            request.user.balance -= cart_total
            request.user.save()
            
            # Lưu lịch sử giao dịch
            Transaction.objects.create(
                user=request.user,
                order=order,
                amount=cart_total,
                transaction_id=f"T{int(time.time())}",
                payment_method='balance',
                status='success',
                description='Thanh toán đơn hàng bằng số dư'
            )
            
            # Xóa giỏ hàng
            cart_items.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Thanh toán thành công',
                'order_id': order.id
            })
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi xử lý thanh toán'
        })

@login_required
def verify_payment(request):
    """Hiển thị trang xác thực thanh toán"""
    # Lấy thông tin 2FA của user
    has_2fa = bool(request.user.two_factor_method)
    two_factor_type = request.user.two_factor_method if has_2fa else None
    
    # Lấy tổng tiền giỏ hàng
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.product.price for item in cart_items)  # Sửa cách tính tổng tiền
    
    # Kiểm tra số dư
    if request.user.balance < cart_total:
        messages.error(request, 'Số dư không đủ để thanh toán')
        return redirect('store:cart')
        
    # Kiểm tra giỏ hàng trống
    if not cart_items.exists():
        messages.error(request, 'Giỏ hàng trống')
        return redirect('store:cart')
    
    context = {
        'has_2fa': has_2fa,
        'two_factor_type': two_factor_type,
        'cart_total': cart_total
    }
    
    return render(request, 'store/verify_payment.html', context)

def trending_suggestions(request):
    """API endpoint for trending searches and recent products"""
    try:
        # Get trending searches
        trending = SearchHistory.objects.values('keyword') \
            .annotate(count=Count('id')) \
            .order_by('-count')[:3]
        
        # Get recently updated products
        recent_products = Product.objects.filter(is_active=True).order_by('-updated_at')[:3]
        
        suggestions = []
        
        # Add trending searches
        for item in trending:
            suggestions.append({
                'type': 'trending',
                'keyword': item['keyword'],
                'count': item['count'],
                'icon': 'fas fa-fire'
            })
        
        # Add recent products with full details
        for product in recent_products:
            try:
                image_url = None
                if product.images.filter(is_primary=True).exists():
                    image_url = product.images.filter(is_primary=True).first().image.url
                elif product.images.exists():
                    image_url = product.images.first().image.url
                else:
                    image_url = static('store/images/default-product.jpg')

                suggestions.append({
                    'type': 'product',
                    'name': product.name,
                    'image': image_url,
                    'price': str(product.price),
                    'url': reverse('store:product_detail', args=[product.id])
                })
            except Exception as e:
                print(f"Error processing product {product.id}: {str(e)}")
                continue
        
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        print(f"Error in trending_suggestions: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def search_suggestions(request):
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'suggestions': []})

        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).distinct()[:5]

        suggestions = []
        for product in products:
            try:
                # Thêm ảnh mặc định nếu không có ảnh
                image_url = None
                if product.images.filter(is_primary=True).exists():
                    image_url = product.images.filter(is_primary=True).first().image.url
                elif product.images.exists():
                    image_url = product.images.first().image.url
                else:
                    image_url = static('store/images/default-product.jpg')

                suggestion = {
                    'type': 'product',
                    'name': product.name,
                    'image': image_url,
                    'price': str(product.price),
                    'url': reverse('store:product_detail', args=[product.id])
                }
                suggestions.append(suggestion)
            except Exception as e:
                print(f"Error processing product {product.id}: {str(e)}")
                continue

        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        print(f"Error in search_suggestions: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def search_products(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'newest')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category:
        products = products.filter(category__slug=category)
        
    if min_price:
        products = products.filter(price__gte=min_price)
        
    if max_price:
        products = products.filter(price__lte=max_price)
        
    if sort == 'bestseller':
        products = products.order_by('-sold_count')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    else:  # newest
        products = products.order_by('-created_at')
        
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort
    }
    
    return render(request, 'store/search_product.html', context)

def trending_searches(request):
    trending = SearchHistory.objects.values('keyword') \
        .annotate(count=Count('id')) \
        .order_by('-count')[:5]
    
    # Get recently updated products
    recent_products = Product.objects.order_by('-updated_at')[:3]
    
    suggestions = []
    
    # Add trending searches
    for item in trending:
        suggestions.append({
            'type': 'trending',
            'keyword': item['keyword'],
            'count': item['count'],
            'icon': 'fas fa-fire'
        })
    
    # Add recent products
    for product in recent_products:
        suggestions.append({
            'type': 'product',
            'keyword': product.name,
            'url': reverse('store:product_detail', args=[product.id]),
            'icon': 'fas fa-clock'
        })
    
    return JsonResponse({'suggestions': suggestions})

# Các hàm API cho chatbot
@csrf_exempt
@require_POST
def log_chat_message(request):
    """API endpoint để lưu lịch sử trò chuyện với chatbot"""
    try:
        data = json.loads(request.body)
        
        session_id = data.get('session_id')
        user_query = data.get('user_query')
        assistant_response = data.get('assistant_response')
        metadata = data.get('metadata', {})
        
        if not session_id or not user_query or not assistant_response:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin bắt buộc'
            }, status=400)
            
        # Lưu log chat vào database
        chat_log = ChatLog.objects.create(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None,
            user_query=user_query,
            response=assistant_response,
            status='success',
            metadata=metadata
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu lịch sử trò chuyện',
            'log_id': chat_log.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        }, status=400)
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử chat: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def rate_chat_message(request):
    """API endpoint để đánh giá chatbot"""
    try:
        data = json.loads(request.body)
        
        session_id = data.get('session_id')
        rating = data.get('rating')
        
        if not session_id or not rating:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin bắt buộc'
            }, status=400)
            
        # Cập nhật đánh giá cho tất cả chatlog trong phiên
        updated = ChatLog.objects.filter(session_id=session_id).update(
            satisfaction_rating=rating
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật đánh giá',
            'updated_logs': updated
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        }, status=400)
    except Exception as e:
        print(f"Lỗi khi cập nhật đánh giá: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def send_chat_feedback(request):
    """API endpoint để gửi góp ý về chatbot"""
    try:
        data = json.loads(request.body)
        
        session_id = data.get('session_id')
        feedback = data.get('feedback')
        rating = data.get('rating')
        
        if not session_id or not feedback:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin bắt buộc'
            }, status=400)
            
        # Lưu góp ý vào database
        chat_feedback = ChatFeedback.objects.create(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None,
            feedback_text=feedback,
            rating=rating or 0
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Đã gửi góp ý thành công',
            'feedback_id': chat_feedback.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ'
        }, status=400)
    except Exception as e:
        print(f"Lỗi khi gửi góp ý: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)

# Thêm các hàm liên quan đến chat
@login_required
def user_chat_dashboard(request):
    """Trang chat cho người dùng"""
    # Import các model cần thiết
    from dashboard.models.conversation import Conversation, Message
    from django.utils import timezone
    from django.shortcuts import get_object_or_404
    
    # Lấy cuộc trò chuyện của người dùng với admin
    conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_time')
    
    # Nếu chưa có cuộc trò chuyện nào, tạo mới với admin mặc định
    if not conversations.exists():
        # Lấy admin mặc định (ví dụ: superuser đầu tiên)
        try:
            default_admin = CustomUser.objects.filter(is_superuser=True).first()
            if default_admin:
                conversation = Conversation.objects.create(
                    admin=default_admin,
                    user=request.user,
                    last_message_time=timezone.now()
                )
                conversation.save()
                
                # Thêm tin nhắn chào mừng
                welcome_message = Message.objects.create(
                    conversation=conversation,
                    sender=default_admin,
                    receiver=request.user,
                    content="Xin chào! Tôi là hỗ trợ viên của TomOi. Bạn cần giúp đỡ gì?",
                    message_type="text"
                )
                welcome_message.save()
                
                # Gán lại conversations là QuerySet thay vì list
                conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_time') 
            else:
                # Không có admin, tạo cuộc trò chuyện không có admin
                conversation = Conversation.objects.create(
                    user=request.user,
                    last_message_time=timezone.now()
                )
                conversation.save()
                # Gán lại conversations là QuerySet thay vì list
                conversations = Conversation.objects.filter(user=request.user).order_by('-last_message_time')
        except Exception as e:
            # Ghi log lỗi
            logger.error(f"Error creating default conversation: {str(e)}")
            conversations = []
    
    # Lấy tin nhắn của cuộc trò chuyện đầu tiên (hoặc được chọn)
    conversation_id = request.GET.get('conversation_id')
    if conversation_id:
        selected_conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    else:
        selected_conversation = conversations.first() if conversations else None
    
    messages_list = []
    if selected_conversation:
        messages_list = Message.objects.filter(conversation=selected_conversation).order_by('sent_at')
        
        # Đánh dấu tin nhắn đã đọc
        unread_messages = messages_list.filter(receiver=request.user, is_read=False)
        for msg in unread_messages:
            msg.mark_as_read()
    
    # Lấy tổng số tin nhắn chưa đọc
    unread_count = Message.objects.filter(
        conversation__user=request.user,
        receiver=request.user,
        is_read=False
    ).count()
    
    context = {
        'conversations': conversations,
        'selected_conversation': selected_conversation,
        'messages': messages_list,
        'unread_count': unread_count
    }
    
    return render(request, 'store/chat/dashboard.html', context)

@login_required
def user_send_message(request):
    """API gửi tin nhắn từ người dùng đến admin"""
    # Import các model cần thiết
    from dashboard.models.conversation import Conversation, Message, UserNotification
    from django.http import JsonResponse
    import json
    import os
    from datetime import datetime
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=400)
    
    # Lấy dữ liệu
    conversation_id = request.POST.get('conversation_id')
    message_content = request.POST.get('message')
    message_type = request.POST.get('message_type', 'text')
    
    if not conversation_id or not message_content:
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin cuộc trò chuyện hoặc nội dung tin nhắn'}, status=400)
    
    # Lấy cuộc trò chuyện
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
    except Conversation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy cuộc trò chuyện'}, status=404)
    
    # Lấy admin của cuộc trò chuyện
    admin = conversation.admin
    if not admin:
        # Nếu chưa có admin, gán admin mặc định
        admin = CustomUser.objects.filter(is_superuser=True).first()
        if not admin:
            return JsonResponse({'status': 'error', 'message': 'Không có quản trị viên nào để gán cho cuộc trò chuyện'}, status=400)
        
        conversation.admin = admin
        conversation.save()
    
    # Xử lý ảnh nếu có
    image_url = None
    if message_type == 'image' and request.FILES.get('image'):
        image = request.FILES['image']
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        upload_path = f'chat_images/{datetime.now().strftime("%Y/%m/%d")}/'
        if not os.path.exists(f'media/{upload_path}'):
            os.makedirs(f'media/{upload_path}', exist_ok=True)
        
        # Lưu file
        file_path = f'{upload_path}{image.name}'
        path = default_storage.save(file_path, ContentFile(image.read()))
        image_url = default_storage.url(path)
        
        # Cập nhật nội dung tin nhắn với URL ảnh
        message_content = image_url
    
    # Tạo tin nhắn mới
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=admin,
        message_type=message_type,
        content=message_content
    )
    
    # Cập nhật thời gian tin nhắn cuối cùng
    conversation.last_message_time = timezone.now()
    conversation.save()
    
    # Tạo thông báo cho admin
    UserNotification.objects.create(
        user=admin,
        message=message
    )
    
    # Trả về thông tin tin nhắn
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'content': message.content,
            'type': message.message_type,
            'sent_at': message.sent_at.strftime('%H:%M'),
            'is_user': True
        }
    })

@require_POST
@csrf_exempt
def update_read_status(request):
    """Cập nhật trạng thái đã đọc tin nhắn cho người dùng"""
    from dashboard.models.conversation import Message
    from django.http import JsonResponse
    import json
    
    try:
        data = json.loads(request.body)
        message_ids = data.get('message_ids', [])
        
        if not message_ids:
            return JsonResponse({'status': 'error', 'message': 'Không có ID tin nhắn nào được cung cấp'})
        
        # Chỉ cập nhật các tin nhắn mà người này là người nhận
        messages = Message.objects.filter(
            id__in=message_ids,
            receiver=request.user,
            is_read=False
        )
        
        for message in messages:
            message.mark_as_read()
            
        return JsonResponse({'status': 'success', 'updated': len(messages)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def get_unread_count(request):
    """Lấy số tin nhắn chưa đọc cho người dùng"""
    from dashboard.models.conversation import Message
    from django.http import JsonResponse
    
    try:
        unread_count = Message.objects.filter(
            conversation__user=request.user,
            receiver=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def acb_qr_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Đơn hàng không tồn tại')
        return redirect('store:order_list')

    if order.payment_status == 'paid':
        messages.info(request, 'Đơn hàng đã được thanh toán')
        return redirect('store:order_detail', order_id=order.id)

    # Tạo transaction mới
    transaction = Transaction.objects.create(
        user=request.user,
        order=order,
        amount=order.total_amount,
        payment_method='acb_qr',
        status='pending'
    )

    # Gọi API ACB để lấy QR code
    try:
        # Thay thế bằng thông tin thực tế của ACB
        acb_api_url = settings.ACB_API_URL
        acb_merchant_id = settings.ACB_MERCHANT_ID
        acb_secret_key = settings.ACB_SECRET_KEY

        # Tạo payload cho API ACB
        payload = {
            'merchantId': acb_merchant_id,
            'orderId': str(transaction.id),
            'amount': int(order.total_amount),
            'currency': 'VND',
            'description': f'Thanh toan don hang #{order.id}',
            'returnUrl': request.build_absolute_uri(reverse('store:acb_qr_return')),
            'cancelUrl': request.build_absolute_uri(reverse('store:acb_qr_cancel')),
        }

        # Ký payload với secret key
        signature = create_acb_signature(payload, acb_secret_key)
        payload['signature'] = signature

        # Gọi API ACB
        response = requests.post(acb_api_url, json=payload)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('code') == '00':
            # Lưu thông tin QR code
            transaction.payment_data = {
                'qr_code': response_data.get('qrCode'),
                'qr_content': response_data.get('qrContent'),
                'expire_time': response_data.get('expireTime')
            }
            transaction.save()

            return render(request, 'store/payment/acb_qr.html', {
                'transaction': transaction,
                'qr_code': response_data.get('qrCode'),
                'qr_content': response_data.get('qrContent'),
                'expire_time': response_data.get('expireTime')
            })
        else:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, 'Không thể tạo mã QR. Vui lòng thử lại sau.')
            return redirect('store:checkout', order_id=order.id)

    except Exception as e:
        transaction.status = 'failed'
        transaction.save()
        messages.error(request, f'Lỗi khi tạo mã QR: {str(e)}')
        return redirect('store:checkout', order_id=order.id)

def acb_qr_return(request):
    transaction_id = request.GET.get('transactionId')
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        if transaction.status == 'pending':
            # Kiểm tra trạng thái thanh toán với ACB
            payment_status = check_acb_payment_status(transaction)
            if payment_status == 'success':
                transaction.status = 'completed'
                transaction.save()
                transaction.order.payment_status = 'paid'
                transaction.order.save()
                messages.success(request, 'Thanh toán thành công')
                return redirect('store:order_detail', order_id=transaction.order.id)
            else:
                transaction.status = 'failed'
                transaction.save()
                messages.error(request, 'Thanh toán thất bại')
                return redirect('store:checkout', order_id=transaction.order.id)
    except Transaction.DoesNotExist:
        messages.error(request, 'Giao dịch không tồn tại')
    return redirect('store:order_list')

def acb_qr_cancel(request):
    transaction_id = request.GET.get('transactionId')
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.status = 'cancelled'
        transaction.save()
        messages.info(request, 'Đã hủy thanh toán')
    except Transaction.DoesNotExist:
        messages.error(request, 'Giao dịch không tồn tại')
    return redirect('store:order_list')

def create_acb_signature(payload, secret_key):
    # Tạo chuỗi để ký
    string_to_sign = '&'.join([f"{k}={v}" for k, v in sorted(payload.items())])
    # Ký với secret key
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def check_acb_payment_status(transaction):
    try:
        # Thay thế bằng thông tin thực tế của ACB
        acb_api_url = settings.ACB_API_URL
        acb_merchant_id = settings.ACB_MERCHANT_ID
        acb_secret_key = settings.ACB_SECRET_KEY

        payload = {
            'merchantId': acb_merchant_id,
            'orderId': str(transaction.id)
        }

        signature = create_acb_signature(payload, acb_secret_key)
        payload['signature'] = signature

        response = requests.post(f"{acb_api_url}/check-status", json=payload)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('code') == '00':
            return 'success' if response_data.get('status') == 'PAID' else 'failed'
        return 'failed'
    except Exception:
        return 'failed'

def bestsellers(request):
    """Hiển thị trang các sản phẩm bán chạy nhất"""
    products = Product.objects.filter(is_active=True).order_by('-sold_count')
    context = {
        'products': products,
        'title': 'Sản phẩm bán chạy',
        'breadcrumb_title': 'Sản phẩm bán chạy'
    }
    return render(request, 'store/featured_products.html', context)

def featured_products(request):
    """Hiển thị trang các sản phẩm nổi bật"""
    products = Product.objects.filter(is_featured=True, is_active=True)
    context = {
        'products': products,
        'title': 'Sản phẩm nổi bật',
        'breadcrumb_title': 'Sản phẩm nổi bật'
    }
    return render(request, 'store/featured_products.html', context)

def newest_products(request):
    """Hiển thị trang các sản phẩm mới nhất"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'products': products,
        'title': 'Sản phẩm mới',
        'breadcrumb_title': 'Sản phẩm mới'
    }
    return render(request, 'store/featured_products.html', context)

def promotions(request):
    """Hiển thị trang các sản phẩm đang khuyến mãi"""
    products = Product.objects.filter(old_price__isnull=False, is_active=True).exclude(old_price=0)
    return render(request, 'store/promotions.html', {
        'products': products
    })

def buying_guide(request):
    """Hiển thị trang hướng dẫn mua hàng"""
    return render(request, 'store/buying_guide.html')

def contact(request):
    """Hiển thị trang liên hệ"""
    return render(request, 'store/contact.html')

def news(request):
    """Hiển thị trang tin tức"""
    posts = BlogPost.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'store/news.html', {
        'posts': posts
    })

@login_required
def check_acb_payment(request, transaction_id):
    """
    Kiểm tra trạng thái thanh toán ACB QR
    """
    try:
        # Lấy thông tin giao dịch
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Kiểm tra xem transaction có thuộc về user hiện tại không
        if transaction.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Bạn không có quyền truy cập giao dịch này'
            })
        
        # Nếu giao dịch đã thành công, trả về kết quả luôn
        if transaction.status == 'success':
            # Chuyển hướng đến trang chi tiết đơn hàng nếu có
            redirect_url = '/orders'
            if transaction.order:
                redirect_url = f'/orders/{transaction.order.id}'
                
            return JsonResponse({
                'status': 'success',
                'message': 'Thanh toán đã được xác nhận',
                'redirect_url': redirect_url
            })
        
        # Kiểm tra trạng thái thanh toán từ ACB
        acb_status = check_acb_payment_status(transaction)
        
        if acb_status == 'success':
            # Cập nhật trạng thái giao dịch
            transaction.status = 'success'
            transaction.save()
            
            # Cập nhật trạng thái đơn hàng nếu có
            if transaction.order:
                transaction.order.payment_status = 'paid'
                transaction.order.save()
            
            # Chuyển hướng đến trang chi tiết đơn hàng nếu có
            redirect_url = '/orders'
            if transaction.order:
                redirect_url = f'/orders/{transaction.order.id}'
                
            return JsonResponse({
                'status': 'success',
                'message': 'Thanh toán thành công',
                'redirect_url': redirect_url
            })
        elif acb_status == 'failed':
            # Cập nhật trạng thái giao dịch
            transaction.status = 'failed'
            transaction.save()
            
            return JsonResponse({
                'status': 'error',
                'message': 'Thanh toán thất bại'
            })
        else:
            # Trạng thái pending
            return JsonResponse({
                'status': 'pending',
                'message': 'Đang chờ thanh toán'
            })
            
    except Transaction.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Không tìm thấy giao dịch'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi: {str(e)}'
        })

@login_required
def add_review(request, product_id):
    """Thêm đánh giá sản phẩm"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        try:
            # Lấy dữ liệu từ form
            rating = int(request.POST.get('rating', 5))
            title = request.POST.get('title', '')
            content = request.POST.get('content', '')
            
            # Kiểm tra nếu người dùng đã đánh giá sản phẩm này chưa
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            
            if existing_review:
                # Cập nhật đánh giá hiện có
                existing_review.rating = rating
                existing_review.title = title
                existing_review.content = content
                existing_review.save()
                messages.success(request, "Đánh giá của bạn đã được cập nhật!")
            else:
                # Tạo đánh giá mới
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    title=title,
                    content=content
                )
                messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
            
            return redirect('store:product_detail', product_id=product_id)
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm đánh giá: {str(e)}")
            messages.error(request, "Có lỗi xảy ra khi gửi đánh giá. Vui lòng thử lại sau.")
    
    return redirect('store:product_detail', product_id=product_id)

@login_required
@require_POST
def apply_tcoin(request):
    try:
        data = json.loads(request.body)
        amount = data.get('amount', 0)
        
        if not amount or int(amount) <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập số TCoin hợp lệ'
            })
        
        # Chuyển đổi sang số nguyên để đảm bảo
        amount = int(amount)
        
        # Kiểm tra người dùng có đủ TCoin không
        if request.user.tcoin < amount:
            return JsonResponse({
                'success': False,
                'message': f'Bạn chỉ có {request.user.tcoin} TCoin'
            })
        
        # Lấy tổng giỏ hàng hiện tại 
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.get_total_price() for item in cart_items)
        
        # Kiểm tra số TCoin tối đa có thể sử dụng
        max_allowed_tcoin = int(cart_total / 100)  # 1 TCoin = 100đ
        
        if amount > max_allowed_tcoin:
            return JsonResponse({
                'success': False,
                'message': f'Số TCoin tối đa có thể sử dụng cho đơn hàng này là {max_allowed_tcoin}'
            })
        
        # Tính số tiền giảm
        discount_amount = amount * 100
        
        # Lưu vào session
        request.session['tcoin_discount'] = discount_amount
        request.session['used_tcoin'] = amount
        
        return JsonResponse({
            'success': True,
            'message': f'Đã áp dụng {amount} TCoin (giảm {discount_amount}đ)',
            'discount_amount': discount_amount
        })
        
    except Exception as e:
        logger.error(f"Error in apply_tcoin: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi áp dụng TCoin'
        })

@login_required
@require_POST
def apply_voucher(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập mã giảm giá'
            })
        
        # Kiểm tra voucher có tồn tại không
        try:
            from accounts.models import Voucher
            voucher = Voucher.objects.get(code=code, is_active=True)
            
            # Kiểm tra voucher còn hạn sử dụng không
            if voucher.expiry_date and voucher.expiry_date < timezone.now().date():
                return JsonResponse({
                    'success': False,
                    'message': 'Mã giảm giá đã hết hạn'
                })
            
            # Kiểm tra số lần sử dụng
            if voucher.max_uses and voucher.used_count >= voucher.max_uses:
                return JsonResponse({
                    'success': False, 
                    'message': 'Mã giảm giá đã hết lượt sử dụng'
                })
                
            # Lấy tổng giỏ hàng hiện tại
            cart_items = CartItem.objects.filter(user=request.user)
            cart_total = sum(item.get_total_price() for item in cart_items)
            
            # Kiểm tra giỏ hàng có đủ giá trị tối thiểu không
            if voucher.min_purchase and cart_total < voucher.min_purchase:
                return JsonResponse({
                    'success': False,
                    'message': f'Giỏ hàng cần tối thiểu {voucher.min_purchase}đ để áp dụng mã này'
                })
            
            # Tính số tiền giảm
            if voucher.discount_type == 'percentage':
                discount_amount = int(cart_total * voucher.discount_value / 100)
                if voucher.max_discount and discount_amount > voucher.max_discount:
                    discount_amount = voucher.max_discount
            else:  # fixed
                discount_amount = voucher.discount_value
            
            # Lưu vào session
            request.session['voucher_code'] = code
            request.session['voucher_discount'] = discount_amount
            request.session['voucher_id'] = voucher.id
            
            return JsonResponse({
                'success': True,
                'message': f'Đã áp dụng mã giảm giá {code}',
                'discount_amount': discount_amount
            })
            
        except Voucher.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mã giảm giá không tồn tại hoặc đã hết hạn'
            })
            
    except Exception as e:
        logger.error(f"Error in apply_voucher: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi áp dụng mã giảm giá'
        })

@login_required
@require_POST
def apply_referral(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập mã giới thiệu'
            })
        
        # Kiểm tra mã giới thiệu có tồn tại không
        try:
            from accounts.models import ReferralCode
            referral = ReferralCode.objects.get(code=code, is_active=True)
            
            # Không thể dùng mã giới thiệu của chính mình
            if referral.user == request.user:
                return JsonResponse({
                    'success': False,
                    'message': 'Bạn không thể sử dụng mã giới thiệu của chính mình'
                })
            
            # Lưu thông tin vào session để xử lý khi thanh toán
            request.session['referral_code'] = code
            request.session['referrer_id'] = referral.user.id
            
            return JsonResponse({
                'success': True,
                'message': 'Đã áp dụng mã giới thiệu thành công'
            })
            
        except ReferralCode.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mã giới thiệu không tồn tại hoặc không hợp lệ'
            })
            
    except Exception as e:
        logger.error(f"Error in apply_referral: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi áp dụng mã giới thiệu'
        })

@login_required
@require_POST
def set_gift_recipient(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập email người nhận'
            })
        
        # Kiểm tra định dạng email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Email không hợp lệ'
            })
        
        # Lưu email người nhận vào session
        request.session['gift_recipient_email'] = email
        
        return JsonResponse({
            'success': True,
            'message': 'Đã xác nhận email người nhận quà'
        })
        
    except Exception as e:
        logger.error(f"Error in set_gift_recipient: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi xác nhận email người nhận'
        })

@login_required
@require_POST
def set_gift_message(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        # Lưu tin nhắn quà tặng vào session
        request.session['gift_message'] = message
        
        return JsonResponse({
            'success': True,
            'message': 'Đã lưu lời nhắn quà tặng'
        })
        
    except Exception as e:
        logger.error(f"Error in set_gift_message: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi lưu lời nhắn'
        })

def gift_demo(request):
    """Hiển thị trang demo mẫu thư quà tặng"""
    
    # Lấy thông tin người dùng nếu đã đăng nhập
    username = request.user.username if request.user.is_authenticated else "Người mua hàng"
    
    # Lấy thông tin sản phẩm từ giỏ hàng nếu có
    product_name = "Spotify Premium 1 tháng"
    
    # Lấy nội dung lời nhắn từ session
    gift_message = request.session.get('gift_message', 'Chúc bạn có trải nghiệm tuyệt vời với món quà này!')
    
    # Lấy email người nhận từ session
    recipient_email = request.session.get('gift_recipient_email', 'nguoinhan@example.com')
    
    context = {
        'username': username,
        'product_name': product_name,
        'gift_message': gift_message,
        'recipient_email': recipient_email
    }
    
    return render(request, 'store/gift_demo.html', context)
