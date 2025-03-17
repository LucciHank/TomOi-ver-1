from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import csv
from datetime import datetime
from django.http import HttpResponse
from store.models import Discount
from django.contrib import messages

def send_order_status_email(order):
    """Send email notification when order status changes"""
    subject = f'Cập nhật trạng thái đơn hàng #{order.id}'
    
    context = {
        'order': order,
        'status': order.get_status_display()
    }
    
    html_message = render_to_string('dashboard/emails/order_status.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=html_message
    )

def export_to_csv(model, filename, fields):
    """
    Hàm xuất dữ liệu ra file CSV
    :param model: Model cần xuất
    :param filename: Tên file xuất
    :param fields: Các trường cần xuất
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(fields)  # Ghi header
    
    for obj in model.objects.all():
        row = []
        for field in fields:
            value = getattr(obj, field)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            row.append(value)
        writer.writerow(row)
    
    return response

def import_from_csv(file, model, field_mapping, request):
    """
    Hàm import dữ liệu từ file CSV
    :param file: File CSV cần import
    :param model: Model cần import vào
    :param field_mapping: Mapping giữa tên cột CSV và tên trường model
    :param request: Request object để thêm messages
    """
    try:
        decoded_file = file.read().decode('utf-8')
        csv_data = csv.DictReader(decoded_file.splitlines())
        
        success_count = 0
        error_count = 0
        
        for row in csv_data:
            try:
                # Chuyển đổi dữ liệu theo mapping
                data = {}
                for csv_field, model_field in field_mapping.items():
                    if csv_field in row:
                        value = row[csv_field]
                        # Xử lý các trường đặc biệt
                        if model_field == 'valid_from' or model_field == 'valid_to':
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        elif model_field == 'value':
                            value = float(value)
                        elif model_field == 'max_uses':
                            value = int(value) if value else None
                        data[model_field] = value
                
                # Tạo hoặc cập nhật object
                if 'code' in data:
                    obj, created = model.objects.update_or_create(
                        code=data['code'],
                        defaults=data
                    )
                else:
                    obj = model.objects.create(**data)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                messages.error(request, f'Lỗi khi import dòng {error_count + success_count}: {str(e)}')
        
        messages.success(request, f'Import thành công {success_count} bản ghi')
        if error_count > 0:
            messages.warning(request, f'Có {error_count} bản ghi bị lỗi')
            
    except Exception as e:
        messages.error(request, f'Lỗi khi đọc file: {str(e)}')
        return False
    
    return True

def is_admin(user):
    """
    Hàm kiểm tra xem người dùng có phải là admin hay không
    :param user: Đối tượng User cần kiểm tra
    :return: True nếu là admin, False nếu không phải
    """
    if user.is_authenticated and user.is_staff:
        return True
    return False 