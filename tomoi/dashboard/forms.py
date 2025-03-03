from django import forms
from store.models import Banner
from .models import Campaign, APIKey, Webhook
from .models.source import Source, SourceLog, SourceProduct
from accounts.models import CustomUser
from django.contrib.auth.models import Group, Permission

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'is_active']

class GeneralSettingsForm(forms.Form):
    site_name = forms.CharField(max_length=100)
    site_description = forms.CharField(widget=forms.Textarea)
    contact_email = forms.EmailField()
    contact_phone = forms.CharField(max_length=20)
    logo = forms.ImageField(required=False)

class EmailSettingsForm(forms.Form):
    smtp_host = forms.CharField(max_length=100)
    smtp_port = forms.IntegerField()
    smtp_username = forms.CharField(max_length=100)
    smtp_password = forms.CharField(widget=forms.PasswordInput)
    smtp_use_tls = forms.BooleanField(required=False)

class PaymentSettingsForm(forms.Form):
    momo_partner_code = forms.CharField(max_length=100)
    momo_access_key = forms.CharField(max_length=100)
    momo_secret_key = forms.CharField(widget=forms.PasswordInput)
    momo_enabled = forms.BooleanField(required=False)
    
    vnpay_terminal_id = forms.CharField(max_length=100)
    vnpay_secret_key = forms.CharField(widget=forms.PasswordInput)
    vnpay_enabled = forms.BooleanField(required=False)

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ['name', 'is_active']

class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = ['url', 'events', 'is_active']
        widgets = {
            'events': forms.CheckboxSelectMultiple
        }

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'url', 'platform', 'product_type', 'base_price',
                 'availability_rate', 'priority', 'notes']
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-select'}),
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
            'processing_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SourceProductForm(forms.ModelForm):
    class Meta:
        model = SourceProduct
        fields = ['source', 'product', 'name', 'description', 'product_url',
                 'price', 'error_rate']
        widgets = {
            'source': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
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

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'address', 'birth_date', 'gender',
                 'is_active', 'user_type', 'avatar']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.FileInput)):
                self.fields[field].widget.attrs['class'] = 'form-control' 

class UserAddForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name',
                 'phone_number', 'address', 'birth_date', 'gender',
                 'user_type', 'avatar', 'is_active']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.FileInput)):
                self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
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
            'first_name', 'last_name', 'email', 'phone_number',
            'avatar', 'account_type', 'is_active', 'is_verified',
            'address', 'bio'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp')

        return cleaned_data

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['role'].initial = self.user.user_type
            self.fields['groups'].initial = self.user.groups.all()
            self.fields['is_staff'].initial = self.user.is_staff
            self.fields['is_superuser'].initial = self.user.is_superuser
            
            # Set initial permissions
            self.fields['product_permissions'].initial = self.user.user_permissions.filter(
                content_type__app_label='store', 
                content_type__model='product'
            )
            self.fields['category_permissions'].initial = self.user.user_permissions.filter(
                content_type__app_label='store',
                content_type__model='category'
            )
            self.fields['order_permissions'].initial = self.user.user_permissions.filter(
                content_type__app_label='store',
                content_type__model='order'
            )
            self.fields['user_permissions'].initial = self.user.user_permissions.filter(
                content_type__app_label='accounts',
                content_type__model='customuser'
            )

    def save(self):
        if not self.user:
            return
            
        # Update role
        self.user.user_type = self.cleaned_data['role']
        
        # Update groups
        self.user.groups.set(self.cleaned_data['groups'])
        
        # Update staff status
        self.user.is_staff = self.cleaned_data['is_staff']
        self.user.is_superuser = self.cleaned_data['is_superuser']
        
        # Update permissions
        permissions = []
        permissions.extend(self.cleaned_data['product_permissions'])
        permissions.extend(self.cleaned_data['category_permissions'])
        permissions.extend(self.cleaned_data['order_permissions'])
        permissions.extend(self.cleaned_data['user_permissions'])
        
        self.user.user_permissions.set(permissions)
        self.user.save() 