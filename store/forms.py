from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Store
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'tu@email.com',
            'id': 'username', 
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '••••••••',
            'id': 'password',
            'type': 'password'
        })
    )
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget= forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': '',
            'id': 'email'
        }))
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre de usuario',
            'id': 'username','autocomplete':'new-password'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered  w-full password-toggle',
            'placeholder': 'Contraseña',
            'id': 'password1','autocomplete':'new-password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered  w-full password-toggle',
            'placeholder': 'Confirmar Contraseñas',
            'id': 'password2','autocomplete':'new-password'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Este email ya está registrado."))
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Este nombre de usuario ya existe."))
        return username

class TiendaForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['nombre', 'ubicacion', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: Supermercado Central'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: Av. Principal 123'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: +56912345678'
            }),
        }
        error_messages = {
            'nombre': {
                'required': "El nombre de la tienda es obligatorio",
            }
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        # Excluye la instancia actual en caso de actualización
        if self.instance.pk:
            if Store.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre).exists():
                raise ValidationError("Ya existe una tienda con este nombre")
        else:
            if Store.objects.filter(nombre__iexact=nombre).exists():
                raise ValidationError("Ya existe una tienda con este nombre")
        return nombre

