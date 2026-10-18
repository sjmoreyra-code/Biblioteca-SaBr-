from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario
from django.db import transaction


def mostrar_index(request):
    return render(request, 'Usuario/index.html')


@login_required
def mostrar_prestamos(request):
    return render(request, 'Usuario/prestamos.html')


@login_required
def mostrar_perfil(request):
    return render(request, 'Usuario/perfil.html', {
        'usuario': request.user
    })


def mostrar_catalogo(request):
    return render(request, 'Usuario/catalogo.html')


def mostrar_detalle_libro(request):
    return render(request, 'Usuario/detalle_libro.html')


@login_required
def mostrar_comunidad(request):
    return render(request, 'Usuario/comunidad.html')


@login_required
def mostrar_historial(request):
    return render(request, 'Usuario/historial.html')


def seleccionar_registro(request):
    return render(request, 'Usuario/seleccionar_registro.html')


def registro_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirmar_password = request.POST.get('confirmar_password', '')

        if not all([nombre, email, username, password, confirmar_password]):
            messages.error(request, 'Completá todos los campos.')
            return render(request, 'Usuario/registro.html')

        if password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'Usuario/registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya está registrado.')
            return render(request, 'Usuario/registro.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Ese correo electrónico ya está registrado.')
            return render(request, 'Usuario/registro.html')

        with transaction.atomic():
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre
                )

            PerfilUsuario.objects.create(
                usuario=usuario,
                nombre=nombre,
                email=email,
                alias=username,
                telefono='',
                direccion=''
                )

        messages.success(
            request,
            'Tu cuenta fue creada correctamente. Ya podés iniciar sesión.'
        )
        return redirect('usuario_login')

    return render(request, 'Usuario/registro.html')


def usuario_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('usuario_index')

        messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'Usuario/login.html')


@login_required
def usuario_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('usuario_login')
    return redirect('usuario_index')