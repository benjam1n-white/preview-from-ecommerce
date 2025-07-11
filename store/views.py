from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import never_cache
from django.http import HttpResponseForbidden, HttpResponseBadRequest,HttpResponse
from .forms import LoginForm, CustomUserCreationForm, TiendaForm
from .models import Profile, Store
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.urls import reverse,reverse_lazy

@method_decorator(ensure_csrf_cookie, name='dispatch')
class TiendaDeleteView(View):
    def delete(self, request, tienda_id):
        try:
            tienda = Store.objects.get(id=tienda_id)
            success, error_msg = tienda.safe_delete()
            
            if success:
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                
        except Store.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tienda no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def eliminar_tienda(request, tienda_id):
    if request.method == "DELETE":
        try:
            tienda = Store.objects.get(id=tienda_id)
            success, error_msg = tienda.safe_delete()
            
            if success:
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                
        except Store.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tienda no encontrada'}, status=404)



def editar_tienda(request, tienda_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No autenticado")
    
    tienda = get_object_or_404(Store, id=tienda_id)
    
    # Verificar que el usuario es propietario de la tienda
    if tienda.propietario != request.user:
        return HttpResponseForbidden("No tienes permiso para editar esta tienda")
    
    if request.method == 'POST':
        form = TiendaForm(request.POST, instance=tienda)
        if form.is_valid():
            try:
                tienda_editada = form.save(commit=False)
                tienda_editada.propietario = request.user
                tienda_editada.full_clean()
                tienda_editada.save()
                # Respuesta para HTMX
                if request.headers.get('HX-Request'):
                    context = {'tienda': tienda_editada}
                    response = render(request, 'partials/tienda_row.html', context)
                    response['HX-Trigger-After-Swap'] = 'closeModal'  # Cerrar modal
                    return response
                
                return redirect('dashboard')
                # context = {'tienda': tienda_editada}
                # return render(request, 'partials/tienda_row.html', context)   
            except ValidationError as e:
                form.add_error(None, e)
                return render(request, 'partials/form_errors.html', {'form': form}, status=400)
        
        return render(request, 'partials/form_errors.html', {'form': form}, status=400)
    
    if request.method == 'GET':
        # Devolver solo el formulario, no el modal completo
        form = TiendaForm(instance=tienda)
        return render(request, 'partials/editar_tienda_form.html', {
            'form': form,
            'tienda': tienda
        })
    



def tienda_create(request):
    # Verificar autenticación
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No autenticado")
    
    # Manejar solicitudes GET (mostrar formulario vacío)
    if request.method == 'GET':
        form = TiendaForm()
        return render(request, 'partials/tienda_form.html', {'form': form})
    
    
    if request.method == 'POST':
        form = TiendaForm(request.POST)
        if form.is_valid():
            tienda = form.save(commit=False)
            tienda.propietario = request.user
            context = {'tienda': tienda, 'success':True }
            try:
                tienda.save()
                response= render(request, 'partials/tienda_row.html', context)
                response['HX-Trigger'] = 'success'
                return response
                
            except ValidationError as e:
                # Capturar errores de validación del modelo
                for error in e:
                    form.add_error(None, error)
        else:
            response = render( request, 'partials/modalsTienda.html', {'form': form})
            response['HX-Retarget'] = '#modalsTiendaForm'
            response['HX-Reswap'] = 'outerHTML'
            response['HX-Trigger-After-Settle'] = 'fail'    
        # Si hay errores, devolver formulario con errores
            return response   
    return HttpResponse("Método no permitido", status=405)


def index(request):
    context = {'form':CustomUserCreationForm(), 'formL':LoginForm() }
    if request.user.is_authenticated:
        context['is_authenticated'] = True
    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if request.headers.get('HX-Request'):
                    # Para solicitudes HTMX, devolver un script que haga la redirección
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('dashboard')
                    return response
                return redirect('dashboard')
        # Si hay errores o no es HTMX, manejar como antes
        return render(request, 'login.html', {'formL': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'formL': form})

@method_decorator([never_cache, csrf_protect, require_http_methods(["GET", "POST"])], name='dispatch')
class Protected(LoginRequiredMixin, View,):
    login_url = '/login/'
    redirect_field_name = 'next'
    template_name = 'dashboard.html'
    max_attempts = 5
    attempt_timeout = 300  # 5 minutos en segundos

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.log_user_activity(request)
        
    def get(self, request, *args, **kwargs):
        next_path= request.GET.get(self.redirect_field_name)
        if not request.path.startswith('/dashboard/'):
            return HttpResponseForbidden("Ruta No Permitida")
        if not self.has_required_permissions(request.user):
            return HttpResponseForbidden("No tienes permiso para acceder a este recurso")
        
        try:
            tiendas=request.user.stores.all()
            context = self.get_context_data()
            context ['tiendas'] = tiendas
            context ['tiendaForm'] = TiendaForm()
            
            return render(request, self.template_name, context)
        except Exception as e:
            print(f'Error en dashboard: {str(e)}')
            return HttpResponseBadRequest("Error al cargar el dashboard")

    def post(self, request, *args, **kwargs):
        """
        Maneja solicitudes POST autenticadas con validación CSRF incorporada
        """
        if not self.has_required_permissions(request.user):
            return HttpResponseForbidden("Acción no permitida")
        return HttpResponseForbidden("Metodo Post No Implementado") 
    def get_context_data(self, **kwargs):
        context = {}  # Obtiene el contexto inicial
        
        context.update({
            'last_login': self.request.user.last_login if self.request.user.is_authenticated else None,
            'session_expiry': self.request.session.get_expiry_age(),
            'security_level': self.calculate_security_level(),
            'form': TiendaForm(),
            'user_role_display': self.get_user_role_display()
        })
        return context

    def has_required_permissions(self, user):
        """
        Verifica permisos adicionales más allá de la autenticación básica
        Incluye verificación del rol del perfil
        """
        if not user.is_authenticated or not user.is_active:
            return False
            
        try:
            profile = user.profile  
            return profile.role in [Profile.Role.ADMIN, Profile.Role.SELLER]  # Solo admin y vendedor
        except Profile.DoesNotExist:
            return False

    def get_user_role_display(self):
        """Obtiene el nombre legible del rol del usuario"""
        try:
            return self.request.user.profile.get_role_display()
        except (Profile.DoesNotExist, AttributeError):
            return "Sin perfil asignado"

    def log_user_activity(self, request):
        if request.user.is_authenticated:
            # En una implementación real, guardaríamos esto en la base de datos
            print(f"Acceso registrado: Usuario {request.user.username} - {request.method} - {request.path}")

    def calculate_security_level(self):
        """Calcula el nivel de seguridad basado en permisos y rol"""
        user = self.request.user
        if not user.is_authenticated:
            return 0
        
        level = 0
        if user.is_staff:
            level += 1
        if user.is_superuser:
            level += 2  # Superusers tienen más nivel que staff
            
        try:
            if user.profile.role == Profile.Role.ADMIN:
                level += 2
            elif user.profile.role == Profile.Role.SELLER:
                level += 1
        except Profile.DoesNotExist:
            pass
        
        return min(max(level, 0), 4) 

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            
            # Crear datos adicionales para la UI
            user_data = {
                'username': user.username,
                'email': user.email,
                
            }
            
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                "registrationSuccess": {
                    "userAuthenticated": True,
                    "userData": user_data
                }
            })
            return response
        else:
            return render(request, 'partials/user_register.html', {'form': form})
    
    return HttpResponse("Método no permitido", status=405)

@require_POST
def logout_view(request):
    logout(request)
    response = HttpResponse()
    response['HX-Redirect'] = reverse('login')  # Redirige a la página de login
    return response
