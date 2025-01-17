from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'phone_number', 'birth_date')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'phone_number', 'birth_date')
        
class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        model = CustomUser
        fields = ['email']

class CustomSetPasswordForm(SetPasswordForm):
    pass

