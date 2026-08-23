from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(required = True, max_length=65, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password = forms.CharField(required = True, max_length=65, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label = "Password", widget=forms.PasswordInput(attrs={'placeholder': 'Create a password'})
    )
    password2 = forms.CharField(label = "Confirm Password", widget=forms.PasswordInput( attrs={'placeholder': 'Re-enter your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }
   
