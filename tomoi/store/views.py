from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import (
    Order, OrderItem, PurchasedAccount, Product, ProductImage, 
    Category, Banner, CartItem, BlogPost, ProductVariant, 
    VariantOption, Wishlist, SearchHistory
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
from django.views.decorators.csrf import ensure_csrf_cookie
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

        return JsonResponse({
            'success': True,
            'message': 'Đã thêm vào giỏ hàng'
        })

    except Exception as e:
        logger.error(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Có lỗi xảy ra khi thêm vào giỏ hàng'
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
