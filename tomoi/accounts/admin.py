from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, AccountType, TCoin, CardTransaction

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color_preview', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'color_code', 'description', 'is_active')
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.color_code,
            obj.name
        )
    color_preview.short_description = 'Xem trước'

    def has_delete_permission(self, request, obj=None):
        # Chỉ admin mới có quyền xóa
        return request.user.user_type == 'admin'

    def has_change_permission(self, request, obj=None):
        # Chỉ admin mới có quyền sửa
        return request.user.user_type == 'admin'

    def has_add_permission(self, request):
        # Chỉ admin mới có quyền thêm
        return request.user.user_type == 'admin'

@admin.register(TCoin)
class TCoinAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'last_updated')
    search_fields = ('user__username', 'user__email')
    
    def save_model(self, request, obj, form, change):
        # Cập nhật số TCoin trong CustomUser
        obj.user.tcoin = obj.amount
        obj.user.save()
        super().save_model(request, obj, form, change)

@admin.register(CardTransaction)
class CardTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'telco', 'amount', 'status', 'created_at')
    list_filter = ('status', 'telco')
    search_fields = ('user__username', 'serial', 'request_id')
    readonly_fields = ('created_at', 'updated_at')

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 
        'email', 
        'full_name',
        'balance_display',
        'tcoin_display',        # Thêm hiển thị TCoin
        'account_label_display',
        'get_status_display',
        'phone_display',
        'date_joined',
        'user_type_display',
    )
    list_filter = ('is_active', 'account_label', 'user_type', 'groups', 'status')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Thông tin đăng nhập', {
            'fields': ('username', 'password', 'email')
        }),
        ('Thông tin cá nhân', {
            'fields': ('first_name', 'last_name', 'avatar', 'phone_number', 'birth_date')
        }),
        ('Quản lý tài khoản', {
            'fields': (
                'is_active',
                'account_label',
                'user_type',
                'status',
                'suspension_reason',
            ),
            'description': 'Quản lý trạng thái và phân loại tài khoản',
        }),
        ('Số dư & TCoin', {
            'fields': ('balance', 'tcoin'),
            'description': 'Quản lý số dư và TCoin của tài khoản',
        }),
        ('Phân quyền nâng cao', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Thông tin hệ thống', {
            'fields': ('join_date', 'last_login', 'last_login_ip', 'failed_login_attempts'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2',
                'user_type',
                'is_active',
                'account_label',
            ),
        }),
    )

    readonly_fields = ('join_date', 'last_login', 'last_login_ip', 'failed_login_attempts', 'tcoin')
    actions = ['activate_users', 'deactivate_users', 'add_balance', 'subtract_balance', 'make_active', 'make_pending', 'make_suspended']

    def full_name(self, obj):
        return obj.get_full_name() or '-'
    full_name.short_description = 'Họ và tên'

    def user_type_display(self, obj):
        colors = {
            'admin': 'purple',
            'staff': 'blue',
            'customer': 'green'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.user_type, 'black'),
            obj.get_user_type_display()
        )
    user_type_display.short_description = 'Chức vụ'

    def account_label_display(self, obj):
        if obj.account_label:
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                obj.account_label.color_code,
                obj.account_label.name
            )
        return '-'
    account_label_display.short_description = 'Loại tài khoản'

    def phone_display(self, obj):
        return obj.phone_number or '-'
    phone_display.short_description = 'Số điện thoại'

    def get_status_display(self, obj):
        status_colors = {
            'active': 'green',
            'pending': 'orange',
            'suspended': 'red'
        }
        status_labels = {
            'active': 'Hoạt động',
            'pending': 'Chờ xác minh',
            'suspended': 'Ngừng hoạt động'
        }
        color = status_colors.get(obj.status, 'gray')
        label = status_labels.get(obj.status, obj.status)
        
        html = f'<span style="color: {color}; font-weight: bold;">{label}</span>'
        if obj.status == 'suspended' and obj.suspension_reason:
            html += f'<br><small style="color: #666">Lý do: {obj.suspension_reason}</small>'
            
        return format_html(html)
    get_status_display.short_description = 'Trạng thái'

    def tcoin_display(self, obj):
        formatted_tcoin = "{:,.0f}".format(obj.tcoin)
        return format_html(
            '<span style="color: #007bff; font-weight: bold;">{}</span>',
            f"{formatted_tcoin} TCoin"
        )
    tcoin_display.short_description = 'TCoin'
    tcoin_display.admin_order_field = 'tcoin'

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Đã kích hoạt {updated} tài khoản.')
    activate_users.short_description = 'Kích hoạt tài khoản đã chọn'

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Đã vô hiệu hóa {updated} tài khoản.')
    deactivate_users.short_description = 'Vô hiệu hóa tài khoản đã chọn'

    def add_balance(self, request, queryset):
        # Thêm logic xử lý thêm tiền vào đây
        amount = request.POST.get('amount', 0)
        try:
            amount = int(amount)
            updated = 0
            for user in queryset:
                user.balance += amount
                user.save()
                updated += 1
            self.message_user(request, f'Đã cộng {amount:,}đ vào {updated} tài khoản.')
        except ValueError:
            self.message_user(request, 'Số tiền không hợp lệ', level='ERROR')
    add_balance.short_description = 'Cộng tiền vào tài khoản đã chọn'

    def subtract_balance(self, request, queryset):
        # Thêm logic xử lý trừ tiền vào đây
        amount = request.POST.get('amount', 0)
        try:
            amount = int(amount)
            updated = 0
            for user in queryset:
                if user.balance >= amount:
                    user.balance -= amount
                    user.save()
                    updated += 1
            self.message_user(request, f'Đã trừ {amount:,}đ từ {updated} tài khoản.')
        except ValueError:
            self.message_user(request, 'Số tiền không hợp lệ', level='ERROR')
    subtract_balance.short_description = 'Trừ tiền từ tài khoản đã chọn'

    def has_view_permission(self, request, obj=None):
        # Admin và staff luôn có quyền xem
        return request.user.is_staff

    def has_add_permission(self, request):
        # Admin luôn có quyền thêm mới
        return request.user.user_type == 'admin'

    def has_change_permission(self, request, obj=None):
        # Admin luôn có quyền sửa
        if request.user.user_type == 'admin':
            return True
        # Staff chỉ có quyền sửa nếu được cấp quyền cụ thể
        if request.user.user_type == 'staff':
            return any([
                request.user.has_perm('accounts.can_change_account_label'),
                request.user.has_perm('accounts.can_manage_user_status'),
                request.user.has_perm('accounts.can_manage_balance')
            ])
        return False

    def has_delete_permission(self, request, obj=None):
        # Chỉ admin mới có quyền xóa
        return request.user.user_type == 'admin'

    def get_readonly_fields(self, request, obj=None):
        if request.user.user_type == 'admin':
            return self.readonly_fields  # Admin không bị giới hạn trường nào
        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.user_type == 'admin':
            return fieldsets  # Admin thấy tất cả các trường
        # Staff không thấy phần phân quyền nâng cao
        return [fs for fs in fieldsets if fs[0] != 'Phân quyền nâng cao']

    def save_model(self, request, obj, form, change):
        if not change:  # Nếu là tạo mới
            # Lấy hoặc tạo loại tài khoản mặc định
            default_type, _ = AccountType.objects.get_or_create(
                code='retail',
                defaults={
                    'name': 'Khách bán lẻ',
                    'color_code': '#666666'
                }
            )
            obj.account_label = default_type
            
        super().save_model(request, obj, form, change)

    # Format hiển thị số dư
    def balance_display(self, obj):
        # Format số dư với dấu phẩy ngăn cách hàng nghìn
        formatted_balance = "{:,.0f}".format(obj.balance)
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{}</span>',
            f"{formatted_balance}đ"
        )
    balance_display.short_description = 'Số dư'
    balance_display.admin_order_field = 'balance'

    def make_active(self, request, queryset):
        queryset.update(status='active')
    make_active.short_description = "Đánh dấu là Hoạt động"
    
    def make_pending(self, request, queryset):
        queryset.update(status='pending')
    make_pending.short_description = "Đánh dấu là Chờ xác minh"
    
    def make_suspended(self, request, queryset):
        if 'apply' in request.POST:
            reason = request.POST.get('suspension_reason')
            updated = queryset.update(
                status='suspended',
                suspension_reason=reason,
                is_active=False  # Tự động vô hiệu hóa tài khoản khi đình chỉ
            )
            self.message_user(request, f'Đã đình chỉ {updated} tài khoản.')
        else:
            return render(
                request,
                'admin/suspend_users.html',
                context={
                    'title': 'Đình chỉ tài khoản',
                    'users': queryset
                }
            )
    make_suspended.short_description = "Đánh dấu là Ngừng hoạt động"

admin.site.register(CustomUser, CustomUserAdmin)