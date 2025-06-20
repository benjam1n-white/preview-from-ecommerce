from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _       
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

class User(AbstractUser):
    pass
class Profile(models.Model):
     
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Cliente')
        SELLER = 'SELLER', _('Vendedor')
        ADMIN = 'ADMIN', _('Administrador')

    user = models.OneToOneField(User, verbose_name=_("rol_usuario"), on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
    max_length=10,  
    choices=Role.choices,
    default=Role.CUSTOMER
)
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = _('perfil')
        verbose_name_plural = _('perfiles')

class Store(models.Model):
    propietario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Cambiado de CASCADE a PROTECT
        related_name='stores',
        verbose_name=_('propietario')
    )
    nombre = models.CharField(_('nombre'), max_length=100)
    ubicacion = models.CharField(_('dirección'), max_length=200)
    telefono = models.CharField(max_length=15)
    

    def clean(self):
        if hasattr(self, 'propietario') and self.propietario:
            if self.propietario.profile.role not in [Profile.Role.SELLER, Profile.Role.ADMIN]:
                raise ValidationError("Solo administradores pueden ser propietarios de tiendas")
    def __str__(self):
        return self.nombre
    

    class Meta:
        verbose_name = _('tienda')
        verbose_name_plural = _('tiendas')
        ordering = ['nombre']
    def safe_delete(self):
        """Eliminación segura con manejo de errores"""
        try:
            self.delete()
            return True, None
        except ProtectedError as e:
            error_msg = _("No se puede eliminar: existen productos asociados")
            return False, error_msg
        except Exception as e:
            return False, str(e)


class Product(models.Model):
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name=_('tienda')
    )
    name = models.CharField(_('nombre'), max_length=100)
    price = models.DecimalField(
        _('precio'),
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]  # No permitir precios negativos
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['name']

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    elif hasattr(instance, 'profile'):
        instance.profile.save()

