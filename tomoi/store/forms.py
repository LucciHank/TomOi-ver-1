from django import forms
from .models import ProductImage, ProductVariant, VariantOption, Product
import json

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']

    def clean(self):
        cleaned_data = super().clean()
        is_primary = cleaned_data.get('is_primary')
        product = self.instance.product
        if is_primary and product.images.filter(is_primary=True).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Only one primary image is allowed per product.")
        return cleaned_data

class ProductAdminForm(forms.ModelForm):
    features_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Tính năng',
        help_text='Nhập danh sách tính năng, mỗi dòng một tính năng',
        required=False
    )

    class Meta:
        model = Product
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nếu có dữ liệu features, chuyển từ list sang text
        instance = kwargs.get('instance')
        if instance and instance.features and isinstance(instance.features, list):
            self.initial['features_text'] = '\n'.join(instance.features)

    def clean(self):
        cleaned_data = super().clean()
        # Xử lý trường features_text để lưu vào features
        features_text = cleaned_data.get('features_text', '')
        if features_text:
            # Chuyển từ text sang list
            features_list = [line.strip() for line in features_text.split('\n') if line.strip()]
            cleaned_data['features'] = features_list
        else:
            cleaned_data['features'] = []
        return cleaned_data

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'product', 'price', 'stock', 'sku', 'is_active']

class VariantOptionForm(forms.ModelForm):
    class Meta:
        model = VariantOption
        fields = ['variant', 'duration', 'price', 'stock', 'is_active']