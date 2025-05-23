from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
from .vnpay import VnPay
from .services.installment_service import InstallmentService
from .models import InstallmentTransaction, Transaction, TransactionItem
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from store.models import CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

def payment_vnpay(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            
            logger.info(f"Starting VNPay payment process for amount: {amount}")
            
            # Tạo mã đơn hàng
            order_id = f"ORDER_{int(time.time())}"
            logger.info(f"Generated order ID: {order_id}")
            
            # Khởi tạo VNPay
            vnpay = VnPay()
            
            # Tạo URL thanh toán
            payment_url = vnpay.get_payment_url(
                amount=amount,
                order_id=order_id,
                order_desc=f"Thanh toan don hang #{order_id}"
            )
            
            logger.info(f"Generated payment URL: {payment_url}")
            
            return JsonResponse({
                'success': True,
                'payment_url': payment_url
            })
            
        except Exception as e:
            logger.error(f"Error in payment_vnpay: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def payment_vnpay_return(request):
    vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
    if vnp_ResponseCode == "00":
        # Thanh toán thành công
        # Cập nhật trạng thái đơn hàng
        return render(request, 'payment/success.html')
    else:
        # Thanh toán thất bại
        return render(request, 'payment/failed.html')

def get_installment_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            
            logger.info(f"Getting installment info for amount: {amount}")
            
            service = InstallmentService()
            result = service.get_installment_info(amount)
            
            if result.get('rspCode') == '00':
                return JsonResponse({
                    'success': True,
                    'data': result.get('data', [])
                })
            else:
                logger.error(f"Error getting installment info: {result.get('rspMsg')}")
                return JsonResponse({
                    'success': False,
                    'error': result.get('rspMsg', 'Unknown error')
                })
            
        except Exception as e:
            logger.error(f"Exception in get_installment_info: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def init_installment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            logger.info(f"Initializing installment payment: {data}")
            
            # Tạo transaction data
            transaction_data = {
                'reqId': int(time.time() * 1000),
                'tmnCode': settings.VNPAY_TMN_CODE,
                'order': {
                    'orderReference': f"ISP_{int(time.time())}",
                    'orderInfo': f"Thanh toan tra gop don hang #{int(time.time())}"
                },
                'transaction': {
                    'issuerCode': data.get('issuerCode'),
                    'scheme': data.get('scheme'),
                    'recurringFrequency': 'monthly',
                    'recurringNumberOfIsp': data.get('numberOfInstallments'),
                    'amount': data.get('amount'),
                    'totalIspAmount': data.get('totalAmount'),
                    'recurringAmount': data.get('recurringAmount'),
                    'currCode': 'VND',
                    'returnUrl': request.build_absolute_uri('/payment/installment-return/'),
                    'cancelUrl': request.build_absolute_uri('/payment/installment-cancel/'),
                    'mcDate': datetime.now().strftime('%Y%m%d%H%M%S')
                },
                'customerInfo': {
                    'forename': request.user.first_name or 'Unknown',
                    'surname': request.user.last_name or 'User',
                    'mobile': request.user.phone or '0123456789',
                    'email': request.user.email,
                    'address': request.user.address or 'Unknown',
                    'city': 'Ha Noi',
                    'country': 'VN'
                },
                'version': '2.1.0',
                'ipAddr': request.META.get('REMOTE_ADDR'),
                'userAgent': request.META.get('HTTP_USER_AGENT')
            }
            
            service = InstallmentService()
            result = service.init_installment(transaction_data)
            
            if result.get('rspCode') == '00':
                # Lưu thông tin transaction
                InstallmentTransaction.objects.create(
                    user=request.user,
                    order_reference=transaction_data['order']['orderReference'],
                    order_info=transaction_data['order']['orderInfo'],
                    amount=data.get('amount'),
                    total_amount=data.get('totalAmount'),
                    recurring_amount=data.get('recurringAmount'),
                    number_of_installments=data.get('numberOfInstallments'),
                    issuer_code=data.get('issuerCode'),
                    scheme=data.get('scheme'),
                    vnpay_transaction_id=result['transaction']['id']
                )
                
                return JsonResponse({
                    'success': True,
                    'data': result
                })
            
            logger.error(f"Error initializing installment: {result.get('rspMsg')}")
            return JsonResponse({
                'success': False,
                'error': result.get('rspMsg', 'Unknown error')
            })
            
        except Exception as e:
            logger.error(f"Exception in init_installment: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

def installment_return(request):
    vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
    if vnp_ResponseCode == "00":
        return render(request, 'payment/success.html')
    else:
        return render(request, 'payment/failed.html')

def installment_cancel(request):
    return render(request, 'payment/failed.html', {
        'message': 'Giao dịch đã bị hủy'
    })

@csrf_exempt
def installment_ipn(request):
    if request.method == 'GET':
        try:
            # Verify hash
            vnp_SecureHash = request.GET.get('vnp_SecureHash')
            if not vnp_SecureHash:
                return JsonResponse({'RspCode': '97', 'Message': 'Invalid signature'})
                
            # Get transaction info
            txn_ref = request.GET.get('vnp_TxnRef')
            amount = request.GET.get('vnp_Amount')
            response_code = request.GET.get('vnp_ResponseCode')
            
            logger.info(f"IPN received for transaction {txn_ref}")
            
            # Find transaction
            transaction = InstallmentTransaction.objects.filter(
                order_reference=txn_ref
            ).first()
            
            if not transaction:
                logger.error(f"Transaction {txn_ref} not found")
                return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})
                
            if transaction.status != 'pending':
                logger.warning(f"Transaction {txn_ref} already processed")
                return JsonResponse({'RspCode': '02', 'Message': 'Order already updated'})
                
            # Update transaction status
            if response_code == '00':
                transaction.status = 'completed'
                logger.info(f"Transaction {txn_ref} completed successfully")
            else:
                transaction.status = 'failed'
                logger.error(f"Transaction {txn_ref} failed with code {response_code}")
                
            transaction.save()
            
            return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
            
        except Exception as e:
            logger.error(f"Error processing IPN: {str(e)}")
            return JsonResponse({'RspCode': '99', 'Message': str(e)})
            
    return JsonResponse({'RspCode': '99', 'Message': 'Invalid request method'})

def qr_payment(request):
    if request.method == 'POST':
        try:
            # Chuyển đổi amount từ string sang decimal
            amount = request.POST.get('amount', '0')
            if not amount or amount == '':
                messages.error(request, 'Số tiền không hợp lệ')
                return redirect('store:cart')
                
            # Chuyển đổi sang số và làm tròn
            amount = round(float(amount))
            
            order_id = f"QR_{int(time.time())}"
            
            # Lấy cart items của user
            cart_items = CartItem.objects.filter(user=request.user)
            
            if not cart_items.exists():
                messages.error(request, 'Giỏ hàng trống')
                return redirect('store:cart')
            
            # Tạo transaction
            transaction = Transaction.objects.create(
                user=request.user,
                order_id=order_id,
                payment_method='qr',
                amount=amount,
                status='pending',
                expired_at=timezone.now() + timedelta(minutes=15)
            )
            
            # Lưu các items
            for item in cart_items:
                variant_name = item.variant.name if item.variant else None
                duration = f"{item.duration} tháng" if item.duration else None
                
                TransactionItem.objects.create(
                    transaction=transaction,
                    product_name=item.product.name,
                    variant_name=variant_name,
                    duration=duration,
                    quantity=item.quantity,
                    price=item.product.price,
                    subtotal=item.quantity * item.product.price
                )
            
            # Tạo QR code URL
            qr_url = f"https://qr.sepay.vn/img?acc=VQRQABHEI5230&bank=MBBank&amount={amount}&des=DH{order_id}"
            
            return render(request, 'payment/qr_payment.html', {
                'amount': amount,
                'order_id': order_id,
                'qr_url': qr_url
            })
            
        except ValueError as e:
            logger.error(f"Error converting amount: {str(e)}")
            messages.error(request, 'Số tiền không hợp lệ')
            return redirect('store:cart')
        except Exception as e:
            logger.error(f"Error in qr_payment: {str(e)}")
            messages.error(request, 'Có lỗi xảy ra khi tạo QR thanh toán')
            return redirect('store:cart')
    
    return redirect('store:cart')

def check_payment_status(request, order_id):
    try:
        transaction = Transaction.objects.get(order_id=order_id)
        
        # Kiểm tra timeout
        if transaction.expired_at and timezone.now() > transaction.expired_at:
            transaction.status = 'expired'
            transaction.error_message = 'Transaction timeout'
            transaction.save()
            return JsonResponse({'status': 'expired'})
            
        if transaction.status == 'completed':
            return JsonResponse({'status': 'completed'})
        elif transaction.status in ['failed', 'expired', 'cancelled']:
            return JsonResponse({'status': transaction.status})
            
        # Kiểm tra với SePay
        service = SePayService()
        is_paid, sepay_transaction_id = service.check_transaction(
            order_id=order_id,
            amount=float(transaction.amount)
        )
        
        if is_paid:
            # Cập nhật transaction
            transaction.status = 'completed'
            transaction.transaction_id = sepay_transaction_id
            transaction.save()
            
            # Xử lý đơn hàng
            process_successful_payment(transaction)
            
            return JsonResponse({'status': 'completed'})
            
        return JsonResponse({'status': 'pending'})
        
    except Transaction.DoesNotExist:
        return JsonResponse({
            'status': 'failed',
            'error': 'Transaction not found'
        })
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })

def process_successful_payment(transaction):
    """Xử lý khi thanh toán thành công"""
    try:
        # Cập nhật số dư của user nếu cần
        if transaction.payment_method == 'balance':
            user = transaction.user
            user.balance -= transaction.amount
            user.save()

        # Xóa giỏ hàng
        CartItem.objects.filter(user=transaction.user).delete()
        
        # Gửi email xác nhận
        send_payment_confirmation_email(transaction)
        
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")
        # Log lỗi nhưng không ảnh hưởng đến trạng thái thanh toán
        pass

@login_required
def vnpay_payment(request):
    """Xử lý thanh toán VNPAY cho nạp tiền"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            
            # Tạo transaction_id duy nhất cho nạp tiền
            transaction_id = f"DEP{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            
            # Tạo transaction mới
            transaction = Transaction.objects.create(
                user=request.user,
                amount=Decimal(amount),
                payment_method='vnpay',
                transaction_id=transaction_id,
                status='pending',
                transaction_type='deposit',  # Đánh dấu là nạp tiền
                expired_at=timezone.now() + timedelta(minutes=15)  # Thêm thời gian hết hạn
            )

            # Tạo URL thanh toán VNPAY
            vnp = VnPay()
            vnp.requestData = {
                'vnp_Version': '2.1.0',
                'vnp_Command': 'pay',
                'vnp_TmnCode': settings.VNPAY_TMN_CODE,
                'vnp_Amount': str(int(Decimal(amount) * 100)),
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_ExpireDate': (datetime.now() + timedelta(minutes=15)).strftime('%Y%m%d%H%M%S'),
                'vnp_CurrCode': 'VND',
                'vnp_IpAddr': get_client_ip(request),
                'vnp_Locale': 'vn',
                'vnp_OrderInfo': f'Nap tien {transaction_id}',
                'vnp_OrderType': 'billpayment',  # Thay đổi loại giao dịch
                'vnp_ReturnUrl': settings.VNPAY_DEPOSIT_RETURN_URL,
                'vnp_TxnRef': transaction_id,
            }

            payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY, is_deposit=True)
            return JsonResponse({
                'success': True,
                'payment_url': payment_url
            })

        except Exception as e:
            logger.error(f"Error in vnpay_payment: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Có lỗi xảy ra trong quá trình xử lý'
            })

    return JsonResponse({
        'success': False,
        'message': 'Phương thức không được hỗ trợ'
    })

# Thêm hàm xử lý IPN từ VNPAY
@csrf_exempt
def vnpay_ipn(request):
    """Xử lý thông báo thanh toán từ VNPAY (IPN URL)"""
    if request.method == 'GET':
        # Lấy các tham số từ request
        input_data = request.GET
        
        if not input_data:
            return JsonResponse({
                'RspCode': '99',
                'Message': 'Invalid request'
            })
            
        # Khởi tạo VnPay và validate dữ liệu
        vnp = VnPay()
        vnp_TxnRef = input_data.get('vnp_TxnRef')
        vnp_ResponseCode = input_data.get('vnp_ResponseCode')
        vnp_TransactionStatus = input_data.get('vnp_TransactionStatus')
        vnp_SecureHash = input_data.get('vnp_SecureHash')
        
        # Tạo data để kiểm tra chữ ký
        vnp_data = {}
        for key, value in input_data.items():
            if key != 'vnp_SecureHash':
                vnp_data[key] = value
                
        # Kiểm tra chữ ký
        is_valid = vnp.validate_response(vnp_data)
        
        if not is_valid:
            return JsonResponse({
                'RspCode': '97',
                'Message': 'Invalid signature'
            })
            
        # Tìm giao dịch trong database
        try:
            transaction = Transaction.objects.get(transaction_id=vnp_TxnRef)
        except Transaction.DoesNotExist:
            return JsonResponse({
                'RspCode': '01',
                'Message': 'Order not found'
            })
            
        # Giao dịch đã được cập nhật trước đó
        if transaction.status in ['completed', 'failed', 'cancelled']:
            return JsonResponse({
                'RspCode': '02',
                'Message': 'Order already updated'
            })
            
        # Kiểm tra mã trả về từ VNPAY
        if vnp_ResponseCode == '00' and vnp_TransactionStatus == '00':
            try:
                # Cập nhật trạng thái giao dịch
                transaction.status = 'completed'
                transaction.save()
                
                # Xử lý giao dịch thành công
                if transaction.transaction_type == 'deposit':
                    # Nạp tiền vào tài khoản người dùng
                    user = transaction.user
                    user.balance += transaction.amount
                    user.save()
                elif transaction.transaction_type == 'order':
                    # Xử lý đơn hàng
                    process_successful_payment(transaction)
                
                return JsonResponse({
                    'RspCode': '00',
                    'Message': 'Confirm Success'
                })
            except Exception as e:
                logger.error(f"Error processing IPN: {str(e)}")
                return JsonResponse({
                    'RspCode': '99',
                    'Message': 'Error processing transaction'
                })
        else:
            # Cập nhật trạng thái thất bại
            transaction.status = 'failed'
            transaction.error_message = f'VNPAY Response Code: {vnp_ResponseCode}'
            transaction.save()
            
            return JsonResponse({
                'RspCode': '00',
                'Message': 'Confirm Success'
            })
                
    return JsonResponse({
        'RspCode': '99',
        'Message': 'Invalid request'
    })

@login_required
def vnpay_order_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            transaction_id = data.get('order_id')

            # Tạo transaction mới
            trans = Transaction.objects.create(
                user=request.user,
                amount=Decimal(amount),
                transaction_id=transaction_id,
                payment_method='vnpay',
                status='pending',
                transaction_type='order'
            )

            # Lưu cart items vào transaction items
            cart_items = CartItem.objects.filter(user=request.user)
            for cart_item in cart_items:
                TransactionItem.objects.create(
                    transaction=trans,
                    product_name=cart_item.product.name,
                    variant_name=cart_item.variant.name if cart_item.variant else None,
                    quantity=cart_item.quantity,
                    price=cart_item.get_price(),
                    duration=cart_item.duration,
                    upgrade_email=cart_item.upgrade_email,
                    account_username=cart_item.account_username
                )

            # Tạo URL thanh toán VNPAY
            vnp = VnPay()
            vnp.requestData = {
                'vnp_Version': '2.1.0',
                'vnp_Command': 'pay',
                'vnp_TmnCode': settings.VNPAY_TMN_CODE,
                'vnp_Amount': str(int(Decimal(amount) * 100)),
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_CurrCode': 'VND',
                'vnp_IpAddr': get_client_ip(request),
                'vnp_Locale': 'vn',
                'vnp_OrderInfo': f'Thanh toan don hang {transaction_id}',
                'vnp_OrderType': 'order',
                'vnp_ReturnUrl': settings.VNPAY_ORDER_RETURN_URL,
                'vnp_TxnRef': transaction_id,
            }

            payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)

            return JsonResponse({
                'code': '00',
                'payment_url': payment_url
            })

        except Exception as e:
            logger.error(f"Error in vnpay_order_payment: {str(e)}")
            return JsonResponse({
                'code': '99',
                'message': 'Có lỗi xảy ra trong quá trình xử lý'
            })

    return JsonResponse({
        'code': '99',
        'message': 'Phương thức không được hỗ trợ'
    })

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_payment_confirmation_email(transaction):
    """Gửi email xác nhận thanh toán"""
    try:
        # Chuẩn bị context cho template email
        context = {
            'user': transaction.user,
            'transaction_id': transaction.transaction_id,
            'amount': transaction.amount,
            'payment_method': transaction.get_payment_method_display(),
            'created_at': transaction.created_at,
            'items': transaction.items.all() if hasattr(transaction, 'items') else [],
        }

        # Render email template
        html_message = render_to_string('payment/email/payment_confirmation.html', context)
        plain_message = strip_tags(html_message)

        # Gửi email
        send_mail(
            subject=f'Xác nhận thanh toán - {transaction.transaction_id}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[transaction.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Sent payment confirmation email for transaction {transaction.transaction_id}")
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {str(e)}")
        
@csrf_exempt
def vnpay_return(request):
    try:
        # Lấy các tham số trả về từ VNPAY
        vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
        vnp_TxnRef = request.GET.get('vnp_TxnRef')
        vnp_Amount = request.GET.get('vnp_Amount')
        vnp_TransactionNo = request.GET.get('vnp_TransactionNo')
        vnp_BankCode = request.GET.get('vnp_BankCode')

        # Tìm transaction trong database
        try:
            transaction = Transaction.objects.get(transaction_id=vnp_TxnRef)
        except Transaction.DoesNotExist:
            messages.error(request, 'Không tìm thấy giao dịch')
            return redirect('store:payment_failed')

        # Kiểm tra mã phản hồi
        if vnp_ResponseCode == "00":
            # Cập nhật trạng thái transaction
            transaction.status = 'completed'
            transaction.save()

            # Gửi email xác nhận
            try:
                send_payment_confirmation_email(transaction)
            except Exception as e:
                logger.error(f"Error sending confirmation email: {str(e)}")

            messages.success(request, 'Thanh toán thành công!')
            return redirect('store:payment_success')
        else:
            # Cập nhật trạng thái thất bại
            transaction.status = 'failed'
            transaction.error_message = f'VNPAY Response Code: {vnp_ResponseCode}'
            transaction.save()

            messages.error(request, 'Thanh toán thất bại')
            return redirect('store:payment_failed')

    except Exception as e:
        logger.error(f"Error in vnpay_return: {str(e)}")
        messages.error(request, 'Có lỗi xảy ra trong quá trình xử lý')
        return redirect('store:payment_failed')