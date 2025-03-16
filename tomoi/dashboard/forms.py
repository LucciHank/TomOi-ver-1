from django import forms
from store.models import Banner, Category
from .models import Campaign, APIKey, Webhook, Source, Product, Discount, WarrantyRequest, WarrantyReason
from .models.source import SourceLog, SourceProduct
from accounts.models import CustomUser
from django.contrib.auth.models import Group, Permission
from django.db.utils import IntegrityError
from .models.user_activity import UserActivityLog
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from datetime import date, datetime, timedelta
import pytz
from store.models import Order, OrderItem, Product
from .models import (
    UserSubscription,
    Source, WarrantyRequest,
    WarrantyReason, WarrantyRequestHistory, WarrantyHistory
)
from .models.conversation import ChatbotConversation
from django.shortcuts import get_object_or_404
import json

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class GeneralSettingsForm(forms.Form):
    site_name = forms.CharField(max_length=100)
    site_description = forms.CharField(widget=forms.Textarea)
    contact_email = forms.EmailField()
    contact_phone = forms.CharField(max_length=20)
    logo = forms.ImageField(required=False)
    favicon = forms.ImageField(required=False)
    footer_text = forms.CharField(widget=forms.Textarea)

class EmailSettingsForm(forms.Form):
    smtp_host = forms.CharField(max_length=100)
    smtp_port = forms.IntegerField()
    smtp_username = forms.CharField(max_length=100)
    smtp_password = forms.CharField(widget=forms.PasswordInput)
    smtp_use_tls = forms.BooleanField(required=False)
    default_from_email = forms.EmailField()

class PaymentSettingsForm(forms.Form):
    momo_partner_code = forms.CharField(max_length=100)
    momo_access_key = forms.CharField(max_length=100)
    momo_secret_key = forms.CharField(widget=forms.PasswordInput)
    momo_enabled = forms.BooleanField(required=False)
    
    vnpay_terminal_id = forms.CharField(max_length=100)
    vnpay_secret_key = forms.CharField(widget=forms.PasswordInput)
    vnpay_enabled = forms.BooleanField(required=False)
    
    bank_transfer_enabled = forms.BooleanField(required=False)
    bank_account_number = forms.CharField(max_length=100, required=False)
    bank_account_name = forms.CharField(max_length=100, required=False)
    bank_name = forms.CharField(max_length=100, required=False)

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = ['url', 'events', 'is_active']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'events': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'url', 'platform', 'product_type', 'base_price',
                 'availability_rate', 'priority', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'availability_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class SourceLogForm(forms.ModelForm):
    class Meta:
        model = SourceLog
        fields = ['source', 'source_product', 'log_type', 'has_stock', 
                 'processing_time', 'notes']
        widgets = {
            'source': forms.Select(attrs={'class': 'form-select'}),
            'source_product': forms.Select(attrs={'class': 'form-select'}),
            'log_type': forms.Select(attrs={'class': 'form-select'}),
            'has_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'processing_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lọc source product theo source được chọn
        if 'source' in self.data:
            try:
                source_id = int(self.data.get('source'))
                self.fields['source_product'].queryset = SourceProduct.objects.filter(source_id=source_id)
            except (ValueError, TypeError):
                pass

class SourceProductForm(forms.ModelForm):
    class Meta:
        model = SourceProduct
        fields = ['source', 'product', 'name', 'description', 'product_url',
                 'price', 'error_rate']
        widgets = {
            'source': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'product_url': forms.URLInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'error_rate': forms.NumberInput(attrs={'class': 'form-control'})
        }

class UserFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'Tất cả trạng thái'),
        ('active', 'Đang hoạt động'),
        ('inactive', 'Vô hiệu'),
    )
    
    USER_TYPE_CHOICES = (
        ('', 'Tất cả loại'),
        ('customer', 'Khách hàng'),
        ('staff', 'Nhân viên'),
        ('admin', 'Admin'),
    )
    
    SOURCE_CHOICES = (
        ('', 'Tất cả nguồn'),
        ('web', 'Website'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    )
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=False)
    source = forms.ChoiceField(choices=SOURCE_CHOICES, required=False)
    search = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select', 'onchange': 'this.form.submit()'})
        self.fields['user_type'].widget.attrs.update({'class': 'form-select', 'onchange': 'this.form.submit()'})
        self.fields['source'].widget.attrs.update({'class': 'form-select', 'onchange': 'this.form.submit()'})
        self.fields['search'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tìm kiếm tên, email, số điện thoại...'
        })

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'address', 'birth_date', 'gender',
                 'is_active', 'user_type', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'user_type': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trường username chỉ đọc nếu đang chỉnh sửa
        if self.instance and self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True

class UserAddForm(forms.ModelForm):
    USER_GROUPS = (
        ('admin', 'Quản trị viên'),
        ('staff', 'Nhân viên'),
        ('collaborator', 'Cộng tác viên'),
        ('customer', 'Khách hàng')
    )

    username = forms.CharField(
        label='Tên đăng nhập',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Nhập tên đăng nhập',
            'id': 'id_username',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Nhập mật khẩu',
            'id': 'id_password',
            'autocomplete': 'new-password'
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email',
            'id': 'id_email'
        })
    )

    phone_number = forms.CharField(
        label='Số điện thoại',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập số điện thoại',
            'id': 'id_phone_number'
        })
    )

    first_name = forms.CharField(
        label='Tên',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên',
            'id': 'id_first_name'
        })
    )

    last_name = forms.CharField(
        label='Họ',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ',
            'id': 'id_last_name'
        })
    )

    bank_account = forms.CharField(
        label='Số tài khoản',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập số tài khoản',
            'id': 'id_bank_account'
        })
    )

    bank_name = forms.CharField(
        label='Tên ngân hàng',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên ngân hàng',
            'id': 'id_bank_name'
        })
    )

    bank_branch = forms.CharField(
        label='Chi nhánh',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập chi nhánh ngân hàng',
            'id': 'id_bank_branch'
        })
    )

    user_group = forms.ChoiceField(
        label='Nhóm người dùng',
        choices=USER_GROUPS,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_user_group'
        })
    )

    is_active = forms.BooleanField(
        label='Kích hoạt tài khoản',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_is_active'
        })
    )

    user_notes = forms.CharField(
        label='Ghi chú',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ghi chú về người dùng',
            'id': 'id_user_notes',
            'rows': 3
        })
    )
    
    referral_code = forms.CharField(
        label='Mã giới thiệu',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã giới thiệu nếu có',
            'id': 'id_referral_code'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'bank_account', 'bank_name', 'bank_branch',
            'is_active', 'user_notes', 'referral_code'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Yêu cầu: tối đa 150 ký tự, chỉ dùng chữ cái, số và các ký tự @/./+/-/_'
        self.fields['password'].help_text = 'Mật khẩu cần ít nhất 8 ký tự, bao gồm chữ, số và ký tự đặc biệt'
        self.fields['is_active'].label_suffix = ''
        self.fields['user_notes'].widget.attrs.update({'rows': '3'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập này đã được sử dụng')
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Mật khẩu cần ít nhất 8 ký tự')
        # Có thể thêm nhiều điều kiện về độ phức tạp của mật khẩu
        return password
    
    def save(self, commit=True):
        # Lưu người dùng với mật khẩu được mã hóa
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        # Thiết lập loại người dùng dựa trên nhóm được chọn
        user_group = self.cleaned_data.get('user_group', 'customer')
        if user_group == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.user_type = 'admin'
        elif user_group == 'staff':
            user.is_staff = True
            user.is_superuser = False
            user.user_type = 'staff'
        elif user_group == 'collaborator':
            user.is_staff = False
            user.is_superuser = False
            user.user_type = 'collaborator'
        else:
            user.is_staff = False
            user.is_superuser = False
            user.user_type = 'customer'
        
        if commit:
            user.save()
            # Xử lý mã giới thiệu nếu có
            referral_code = self.cleaned_data.get('referral_code')
            if referral_code:
                referred_user = CustomUser.objects.filter(referral_code=referral_code).first()
                if referred_user:
                    user.referred_by = referred_user
                    user.save(update_fields=['referred_by'])
        return user

class UserForm(forms.ModelForm):
    """Form chỉnh sửa thông tin người dùng"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text='Để trống nếu không muốn thay đổi mật khẩu'
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='Xác nhận mật khẩu'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'gender', 
            'birth_date', 
            'account_type',  # Bỏ field 'role' vì không có trong model
            'bio'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            self.add_error('confirm_password', 'Mật khẩu xác nhận không khớp')
            
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập này đã được sử dụng')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
            
        return user

class UserPermissionForm(forms.Form):
    """Form phân quyền người dùng"""
    
    role = forms.ChoiceField(
        choices=[
            ('staff', 'Nhân viên'),
            ('admin', 'Quản trị viên'),
            ('user', 'Người dùng')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Vai trò'
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
        label='Nhóm người dùng'
    )

    is_staff = forms.BooleanField(
        required=False,
        label='Quyền quản trị',
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'})
    )

    is_superuser = forms.BooleanField(
        required=False,
        label='Quyền quản trị cao cấp',
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'})
    )

    # Quyền cho từng module
    product_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='store', content_type__model='product'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox product-permission'}),
        required=False,
        label='Quyền quản lý sản phẩm'
    )

    category_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='store', content_type__model='category'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox product-permission'}),
        required=False,
        label='Quyền quản lý danh mục'
    )

    order_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='store', content_type__model='order'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox order-permission'}),
        required=False,
        label='Quyền quản lý đơn hàng'
    )

    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='accounts', content_type__model='customuser'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox user-permission'}),
        required=False,
        label='Quyền quản lý người dùng'
    )
    
    report_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(content_type__app_label='dashboard', content_type__model='report'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox report-permission'}),
        required=False,
        label='Quyền báo cáo'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Điền dữ liệu hiện tại
            self.fields['is_staff'].initial = user.is_staff
            self.fields['is_superuser'].initial = user.is_superuser
            
            # Vai trò
            if user.is_superuser:
                self.fields['role'].initial = 'admin'
            elif user.is_staff:
                self.fields['role'].initial = 'staff'
            else:
                self.fields['role'].initial = 'user'
                
            # Nhóm
            self.fields['groups'].initial = user.groups.all()
            
            # Các quyền
            user_perms = user.user_permissions.all()
            self.fields['product_permissions'].initial = [p for p in user_perms if p in self.fields['product_permissions'].queryset]
            self.fields['category_permissions'].initial = [p for p in user_perms if p in self.fields['category_permissions'].queryset]
            self.fields['order_permissions'].initial = [p for p in user_perms if p in self.fields['order_permissions'].queryset]
            self.fields['user_permissions'].initial = [p for p in user_perms if p in self.fields['user_permissions'].queryset]
            self.fields['report_permissions'].initial = [p for p in user_perms if p in self.fields['report_permissions'].queryset]
    
    def save(self):
        # Cần phải cập nhật người dùng từ view
        pass

class WarrantyRequestForm(forms.ModelForm):
    """Form yêu cầu bảo hành từ người dùng"""
    custom_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Lý do khác"
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Ghi chú"
    )
    
    is_self_registered = forms.BooleanField(
        required=False,
        label="Tự đăng ký",
        help_text="Đánh dấu nếu bạn đã tự đăng ký tài khoản này"
    )
    
    class Meta:
        model = WarrantyRequest
        fields = [
            'order', 'account_username', 'account_password', 'account_type',
            'reason', 'custom_reason', 'error_screenshot', 'notes',
            'platform', 'source', 'is_self_registered'
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-select'}),
            'account_username': forms.TextInput(attrs={'class': 'form-control'}),
            'account_password': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Lọc đơn hàng chỉ của người dùng đăng nhập
        if user:
            self.fields['order'].queryset = Order.objects.filter(user=user).order_by('-created_at')
            
        # Lọc lý do bảo hành đang hoạt động
        self.fields['reason'].queryset = WarrantyReason.objects.filter(is_active=True)
        
        # Lọc nguồn đang hoạt động
        self.fields['source'].queryset = Source.objects.filter(is_active=True)

class WarrantyProcessForm(forms.Form):
    """Form xử lý yêu cầu bảo hành"""
    WARRANTY_TYPE_CHOICES = WarrantyRequestHistory.WARRANTY_TYPE_CHOICES
    
    warranty_types = forms.MultipleChoiceField(
        choices=WARRANTY_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Hình thức bảo hành"
    )
    
    added_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        required=False,
        initial=0,
        label="Số ngày bù thêm"
    )
    
    refund_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        required=False,
        initial=0,
        label="Số tiền hoàn trả"
    )
    
    new_account_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label="Tên đăng nhập tài khoản mới"
    )
    
    new_account_password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label="Mật khẩu tài khoản mới"
    )
    
    status = forms.ChoiceField(
        choices=WarrantyRequest.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Trạng thái"
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Ghi chú"
    )
    
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Ghi chú nội bộ (chỉ admin thấy)"
    )

class ProductForm(forms.ModelForm):
    primary_image = forms.ImageField(required=False, label='Ảnh chính')
    additional_images = forms.ImageField(
        required=False,
        label='Hình ảnh bổ sung',
        help_text='Tải lên từng ảnh riêng lẻ'
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'old_price', 'stock', 
            'category', 'brand', 'label', 'product_code', 'duration',
            'features', 'is_featured', 'is_active', 'requires_email',
            'requires_account_password', 'is_cross_sale', 'cross_sale_products',
            'cross_sale_discount'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'label': forms.Select(attrs={'class': 'form-select'}),
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-select'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_account_password': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_cross_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cross_sale_products': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'cross_sale_discount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm các lớp và placeholder
        self.fields['name'].widget.attrs.update({'placeholder': 'Nhập tên sản phẩm'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Mô tả chi tiết về sản phẩm'})
        self.fields['price'].widget.attrs.update({'placeholder': 'Giá hiện tại'})
        self.fields['old_price'].widget.attrs.update({'placeholder': 'Giá cũ (nếu có)'})
        self.fields['product_code'].widget.attrs.update({'placeholder': 'Mã sản phẩm/SKU'})
        self.fields['cross_sale_discount'].widget.attrs.update({'placeholder': 'Phần trăm giảm giá khi mua kèm'})
        
        # Tuỳ chỉnh các trường không bắt buộc
        self.fields['old_price'].required = False
        self.fields['brand'].required = False
        self.fields['label'].required = False
        self.fields['features'].required = False
        self.fields['product_code'].required = False
        self.fields['cross_sale_products'].required = False
        
    def clean_features(self):
        """Chuyển đổi features từ dạng text sang dạng list"""
        features = self.cleaned_data.get('features')
        
        # Nếu features là chuỗi, chuyển đổi thành list
        if isinstance(features, str):
            return [f.strip() for f in features.split('\n') if f.strip()]
        
        return features 

class CategoryForm(forms.ModelForm):
    """Form quản lý danh mục sản phẩm"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'parent', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên danh mục'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả danh mục'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Đường dẫn tĩnh'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loại bỏ danh mục hiện tại khỏi các lựa chọn parent (để tránh chọn chính nó làm parent)
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)
            # Đánh dấu trường parent là không bắt buộc
            self.fields['parent'].required = False