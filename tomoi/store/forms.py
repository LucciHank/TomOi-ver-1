from django import forms
from .models import ProductImage, Product, ProductVariant, VariantOption

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

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'product', 'is_active', 'order']

class VariantOptionForm(forms.ModelForm):
    class Meta:
        model = VariantOption
        fields = ['variant', 'duration', 'price', 'stock', 'is_active']