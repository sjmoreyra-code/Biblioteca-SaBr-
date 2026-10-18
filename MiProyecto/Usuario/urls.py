
from django.urls import path
from Usuario import views

urlpatterns = [
    path('', views.mostrar_index, name='usuario_index'),
    path('prestamos/', views.mostrar_prestamos, name='usuario_prestamos'),
    path('perfil/', views.mostrar_perfil, name='usuario_perfil'),
    path('catalogo/', views.mostrar_catalogo, name='usuario_catalogo'),
    path('detalle-libro/', views.mostrar_detalle_libro, name='usuario_detalle_libro'),
    path('comunidad/', views.mostrar_comunidad, name='usuario_comunidad'),
    path('historial/', views.mostrar_historial, name='usuario_historial'),

    path('seleccionar-registro/', views.seleccionar_registro, name='seleccionar_registro'),
    path('registro/', views.registro_usuario, name='usuario_registro'),
    path('login/', views.usuario_login, name='usuario_login'),
    path('logout/', views.usuario_logout, name='usuario_logout'),
]
