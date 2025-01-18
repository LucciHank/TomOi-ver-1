from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Order, PurchasedAccount, Product, ProductImage,  Category
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
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# from paypalrestsdk import Payment
# import paypalrestsdk

def dashboard(request):
    return render(request, 'store/index.html')

def home(request):
    return render(request, 'store/home.html')

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

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            validate_email(email)  # Xác thực email hợp lệ
            user = CustomUser.objects.get(email=email)
            otp = random.randint(100000, 999999)
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                'tomoivn2024@gmail.com',
                [email],
            )
            request.session['otp'] = otp
            request.session['otp_created_at'] = datetime.now().isoformat()
            return JsonResponse({'success': True, 'message': 'OTP sent to your email'})
        except ValidationError:
            return JsonResponse({'success': False, 'message': 'Invalid email format'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email does not exist'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        created_at = request.session.get('otp_created_at')

        # Kiểm tra thời gian hết hạn (5 phút)
        if not created_at or datetime.fromisoformat(created_at) + timedelta(minutes=5) < datetime.now():
            return JsonResponse({'success': False, 'message': 'OTP has expired'})

        if otp == stored_otp:
            del request.session['otp']
            del request.session['otp_created_at']
            return JsonResponse({'success': True, 'message': 'Mã OTP hợp lệ!'})
        return JsonResponse({'success': False, 'message': 'Mã OTP không hợp lệ, vui lòng thử lại!'})

def resend_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = random.randint(100000, 999999)  # Generate a new 6-digit OTP
            # Send the new OTP via email
            send_mail(
                'Your OTP Code',
                f'Your new OTP code is {otp}',
                'tomoivn2024@gmail.com',  # Replace with your email sender address
                [email],
            )
            # Store the new OTP in the session
            request.session['otp'] = otp
            return JsonResponse({'success': True, 'message': 'OTP has been resent to your email'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email does not exist'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

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
# Lấy các sản phẩm trong giỏ
def cart_view(request):
    cart_items = request.session.get('cart_items', [])
    total_price = sum(item['total_price'] for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            data = json.loads(request.body)  # Đọc dữ liệu JSON từ request body

            # Kiểm tra stock nếu cần
            if int(data.get('stock')) <= 0:
                return JsonResponse({'success': False, 'message': 'Sản phẩm hết hàng'})

            cart_items = request.session.get('cart_items', [])

            # Kiểm tra nếu sản phẩm đã có trong giỏ
            for item in cart_items:
                if item['product_id'] == product.id:
                    item['quantity'] += 1
                    item['total_price'] = item['quantity'] * float(product.price)  # Chuyển price sang float
                    break
            else:
                cart_items.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': float(product.price),  # Chuyển price sang float
                    'quantity': 1,
                    'total_price': float(product.price),  # Chuyển price sang float
                })

            request.session['cart_items'] = cart_items

            # Cập nhật stock
            new_stock = product.stock - 1
            product.stock = new_stock
            product.save()

            return JsonResponse({'success': True, 'cart': cart_items, 'new_stock': new_stock})
        
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Sản phẩm không tồn tại.'})

    else:
        return JsonResponse({'success': False, 'message': 'Chỉ hỗ trợ phương thức POST'})


@login_required
def get_cart_api(request):
    cart_items = request.session.get('cart_items', [])
    # Cập nhật tổng số lượng và tổng giá trị cho giỏ hàng
    total_items = sum(item['quantity'] for item in cart_items)
    return JsonResponse({
        'cart': cart_items,
        'total_items': total_items
    })

# Xóa sản phẩm khỏi giỏ
def remove_from_cart(request, item_id):
    cart_items = request.session.get('cart_items', [])
    cart_items = [item for item in cart_items if item['product_id'] != int(item_id)]
    request.session['cart_items'] = cart_items
    return redirect('store:cart')

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