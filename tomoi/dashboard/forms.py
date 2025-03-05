from django import forms
from store.models import Banner
from .models import Campaign, APIKey, Webhook
from .models.source import Source, SourceLog, SourceProduct
from accounts.models import CustomUser
from django.contrib.auth.models import Group, Permission
from django.db.utils import IntegrityError
from .models.user_activity import UserActivityLog

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
            'rows': 3,
            'placeholder': 'Nhập ghi chú nếu có',
            'id': 'id_user_notes'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'password',
            'first_name', 'last_name', 'is_active', 'user_group',
            'bank_account', 'bank_name', 'bank_branch', 'user_notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đặt label tiếng Việt
        self.fields['email'].label = 'Email'
        self.fields['phone_number'].label = 'Số điện thoại'
        self.fields['password'].label = 'Mật khẩu'
        self.fields['first_name'].label = 'Tên'
        self.fields['last_name'].label = 'Họ'
        self.fields['is_active'].label = 'Kích hoạt tài khoản'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Tên đăng nhập không được để trống")
        if len(username) < 3:
            raise forms.ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập này đã được sử dụng")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Mật khẩu không được để trống")
        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        # Set user type based on group
        group = self.cleaned_data['user_group']
        if group == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif group in ['staff', 'collaborator']:
            user.is_staff = True
            user.is_superuser = False
        
        if commit:
            try:
                user.save()
                # Tạo log
                if hasattr(self, 'admin_user'):
                    UserActivityLog.objects.create(
                        user=user,
                        admin=self.admin_user,
                        action_type='create',
                        description=f'Tạo mới người dùng {user.username}'
                    )
            except IntegrityError as e:
                raise forms.ValidationError(f'Có lỗi xảy ra khi tạo người dùng: {str(e)}')
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
            'bio': forms.Textarea(attrs={'rows': 3}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username == self.instance.username:
            return username
            
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập này đã được sử dụng')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
            
        if commit:
            try:
                user.save()
                # Log thay đổi nếu có admin user
                if hasattr(self, 'admin_user'):
                    changes = []
                    for field in self.changed_data:
                        old_value = getattr(self.instance, field)
                        new_value = self.cleaned_data[field]
                        if old_value != new_value:
                            changes.append(f"{field}: {old_value} -> {new_value}")
                    
                    if changes:
                        UserActivityLog.objects.create(
                            user=user,
                            admin=self.admin_user,
                            action_type='update',
                            description=f'Cập nhật thông tin: {", ".join(changes)}'
                        )
            except Exception as e:
                raise forms.ValidationError(f'Có lỗi xảy ra khi lưu thông tin: {str(e)}')
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