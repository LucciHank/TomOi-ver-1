from django import forms
from store.models import Banner
from .models import Campaign, APIKey, Webhook
from .models.source import Source, SourceLog, SourceProduct

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
        fields = ['name', 'url', 'platform', 'product_type', 'base_price', 'availability_rate', 'priority', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'availability_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SourceLogForm(forms.ModelForm):
    class Meta:
        model = SourceLog
        fields = ['source', 'status', 'price', 'processing_time', 'notes']
        widgets = {
            'source': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'processing_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SourceProductForm(forms.ModelForm):
    class Meta:
        model = SourceProduct
        fields = ['source', 'product', 'name', 'description', 'product_url', 'price', 'error_rate'] 