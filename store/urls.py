from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('Register/', views.register, name='sqrt'),
    path('Nueva/', views.tienda_create, name='creat'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.Protected.as_view(), name='dashboard'),
    path('tienda/editar/<int:tienda_id>/', views.editar_tienda, name='editar_tienda'),
    # path('tienda/eliminar/<int:tienda_id>/', views.eliminar_tienda, name='eliminar_tienda'),
    path('tienda/eliminar/<int:tienda_id>/', views.TiendaDeleteView.as_view(), name='eliminar_tienda'),
   
]
