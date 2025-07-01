from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:border-yellow-400'
    }))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:border-yellow-400'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:border-yellow-400'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:border-yellow-400'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:border-yellow-400'}),
        }
