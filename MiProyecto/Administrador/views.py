from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ProtectedError
from Administrador.models import *
from .forms import CrearUsuariosForm, CrearLibrosForm, CrearPrestamosForm
from django.db import transaction, OperationalError
from django.db.models import F

# ==========================
# ACTUALIZAR DISPONIBILIDAD DE LIBROS
# ==========================


def actualizar_disponibilidad(libro):
    tiene_prestamos_pendientes = Prestamos.objects.filter(
        libro=libro,
        fecha_devolucion_real__isnull=True
    ).exists()

    libro.disponibilidad = not tiene_prestamos_pendientes
    libro.save(update_fields=['disponibilidad'])


# ==========================
# PÁGINAS PRINCIPALES
# ==========================

def mostrar_index(request):
    libros = Libros.objects.all()
    context = {'libros': libros}
    return render(request, 'Administrador/index.html', context=context)


def mostrar_quienes_somos(request):
    return render(request, 'Administrador/quienes_somos.html')


def mostrar_registro(request):
    return render(request, 'Administrador/seleccionar_registro.html')


def mostrar_accesibilidad(request):
    return render(request, 'Administrador/accesibilidad.html')


# ==========================
# GESTIÓN DE LIBROS
# ==========================
@staff_member_required
def mostrar_libros(request):
    libros = Libros.objects.all()
    context = {'libros': libros}
    return render(request, 'Administrador/libros.html', context=context)

@staff_member_required
def crear_libro(request):
    """
    Vista para procesar la creación de un nuevo Libro.
    """
    if request.method == 'POST':
        form = CrearLibrosForm(request.POST)

        if form.is_valid():
            libro_creado = form.save()

            messages.success(
                request,
                f'Libro "{libro_creado.titulo_libro}" creado con éxito.'
            )

            return redirect('libros')
    else:
        form = CrearLibrosForm()

    return render(
        request,
        'Administrador/crear_libros.html',
        {'form': form}
    )


def buscar_libros(request):
    termino = request.GET.get('buscar', '').strip()
    libros = Libros.objects.filter(titulo_libro__icontains=termino)

    return render(
        request,
        'Administrador/buscar_libros.html',
        {'libros': libros}
    )

@staff_member_required
def editar_libro(request, id):
    libro = get_object_or_404(Libros, id=id)

    if request.method == 'POST':
        form = CrearLibrosForm(request.POST, instance=libro)

        if form.is_valid():
            libro_editado = form.save()

            messages.success(
                request,
                f'Libro "{libro_editado.titulo_libro}" actualizado con éxito.'
            )

            return redirect('libros')
    else:
        form = CrearLibrosForm(instance=libro)

    return render(
        request,
        'Administrador/editar_libro.html',
        {'form': form, 'libro': libro}
    )



@staff_member_required
def eliminar_libro(request, id):
    libro = get_object_or_404(Libros, id=id)


    if request.method == 'POST':
        titulo_libro = libro.titulo_libro

        try:
            libro.delete()
            messages.success(
                request,
                f'Libro "{titulo_libro}" eliminado con éxito.'
            )
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar el libro "{titulo_libro}" '
                'porque tiene préstamos asociados.'
            )

        return redirect('libros')

    return render(
        request,
        'Administrador/eliminar_libro.html',
        {'libro': libro}
    )


# ==========================
# GESTIÓN DE USUARIOS
# ==========================
@staff_member_required
def mostrar_usuarios(request):
    usuario = Usuarios.objects.all()
    context = {'usuario': usuario}

    return render(
        request,
        'Administrador/usuarios.html',
        context=context
    )

@staff_member_required
def crear_usuario(request):
    """
    Vista para procesar el registro de un nuevo Usuario.
    """
    if request.method == 'POST':
        form = CrearUsuariosForm(request.POST)

        if form.is_valid():
            usuario_creado = form.save()

            messages.success(
                request,
                f'Usuario "{usuario_creado.nombre_usuario}" registrado con éxito.'
            )

            return redirect('usuarios')
    else:
        form = CrearUsuariosForm()

    return render(
        request,
        'Administrador/crear_usuarios.html',
        {'form': form}
    )

@staff_member_required
def buscar_usuarios(request):
    termino = request.GET.get('buscar', '').strip()

    usuarios = Usuarios.objects.filter(
        nombre_usuario__icontains=termino
    ) | Usuarios.objects.filter(
        email_usuario__icontains=termino
    )

    return render(
        request,
        'Administrador/buscar_usuarios.html',
        {'usuario': usuarios, 'termino': termino}
    )

@staff_member_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuarios, id=id)

    if request.method == 'POST':
        form = CrearUsuariosForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Usuario "{usuario.nombre_usuario}" actualizado con éxito.'
            )

            return redirect('usuarios')
    else:
        form = CrearUsuariosForm(instance=usuario)

    return render(
        request,
        'Administrador/editar_usuario.html',
        {'form': form, 'usuario': usuario}
    )


@staff_member_required
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuarios, id=id)

    if request.method == 'POST':
        nombre_usuario = usuario.nombre_usuario

        try:
            usuario.delete()
            messages.success(
                request,
                f'Usuario "{nombre_usuario}" eliminado con éxito.'
            )
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar el usuario "{nombre_usuario}" '
                'porque tiene préstamos asociados.'
            )

        return redirect('usuarios')

    return render(
        request,
        'Administrador/eliminar_usuario.html',
        {'usuario': usuario}
    )



# ==========================
# GESTIÓN DE PRÉSTAMOS
# ==========================



def actualizar_disponibilidad_libro(libro):
    """
    Un libro está disponible si no tiene préstamos activos.
    Un préstamo sigue activo hasta que se registra su devolución real.
    """

    tiene_prestamo_activo = Prestamos.objects.filter(
        libro=libro,
        fecha_devolucion_real__isnull=True
    ).exists()

    libro.disponibilidad = not tiene_prestamo_activo
    libro.save(update_fields=['disponibilidad'])




@staff_member_required
def mostrar_prestamos(request):
    prestamos = Prestamos.objects.all()
    error_fechas = False

    for prestamo in prestamos:
        prestamo.error_fechas = (
            prestamo.fecha_devolucion_prevista is not None
            and prestamo.fecha_devolucion_prevista < prestamo.fecha_prestamo
        )

        if prestamo.error_fechas:
            error_fechas = True

        prestamo.devolucion_registrada = (
            prestamo.fecha_devolucion_real is not None
        )

    context = {
        'prestamos': prestamos,
        'error_fechas': error_fechas,
    }

    return render(
        request,
        'Administrador/prestamos.html',
        context=context
    )


@staff_member_required
def crear_prestamo(request):
    if request.method == 'POST':
        form = CrearPrestamosForm(request.POST)

        if form.is_valid():
            libro_id = form.cleaned_data['libro'].pk

            try:
                with transaction.atomic():
                    # Forzar una escritura para obtener el bloqueo
                    # de escritura de SQLite antes de comprobar.
                    Libros.objects.filter(pk=libro_id).update(
                        disponibilidad=F('disponibilidad')
                    )

                    # Volver a consultar el estado actualizado.
                    libro = Libros.objects.get(pk=libro_id)

                    tiene_prestamo_activo = Prestamos.objects.filter(
                        libro=libro,
                        fecha_devolucion_real__isnull=True
                    ).exists()

                    if not libro.disponibilidad or tiene_prestamo_activo:
                        form.add_error(
                            'libro',
                            'Este libro acaba de ser prestado '
                            'y ya no está disponible. Elegí otro libro.'
                        )
                    else:
                        prestamo = form.save(commit=False)
                        prestamo.libro = libro
                        prestamo.save()

                        actualizar_disponibilidad_libro(libro)

                if form.errors:
                    pass
                else:
                    messages.success(
                        request,
                        'Préstamo registrado con éxito.'
                    )
                    return redirect('prestamos')

            except OperationalError:
                form.add_error(
                    None,
                    'No se pudo registrar el préstamo en este momento. '
                    'Volvé a intentarlo.'
                )

    else:
        form = CrearPrestamosForm()

    return render(
        request,
        'Administrador/crear_prestamos.html',
        {'form': form}
    )

@staff_member_required
def editar_prestamo(request, id):
    prestamo = get_object_or_404(Prestamos, id=id)
    libro_anterior = prestamo.libro

    if request.method == 'POST':
        form = CrearPrestamosForm(
            request.POST,
            instance=prestamo
        )

        if form.is_valid():
            prestamo = form.save()

            actualizar_disponibilidad_libro(libro_anterior)
            actualizar_disponibilidad_libro(prestamo.libro)

            messages.success(
                request,
                'Préstamo actualizado con éxito.'
            )
            return redirect('prestamos')

    else:
        form = CrearPrestamosForm(instance=prestamo)

    return render(
        request,
        'Administrador/editar_prestamo.html',
        {
            'form': form,
            'prestamo': prestamo
        }
    )

@staff_member_required
def eliminar_prestamo(request, id):
    prestamo = get_object_or_404(Prestamos, id=id)

    if request.method == 'POST':

        # Impedir eliminar préstamos pendientes de devolución.
        if prestamo.fecha_devolucion_real is None:
            messages.error(
                request,
                'No se puede eliminar este préstamo porque '
                'está pendiente de devolución. Registrá la '
                'devolución antes de eliminarlo.'
            )
            return redirect('prestamos')

        libro = prestamo.libro
        prestamo.delete()

        actualizar_disponibilidad_libro(libro)

        messages.success(
            request,
            'Préstamo eliminado con éxito.'
        )
        return redirect('prestamos')

    return render(
        request,
        'Administrador/eliminar_prestamo.html',
        {'prestamo': prestamo}
    )


@staff_member_required
def registrar_devolucion(request, id):
    prestamo = get_object_or_404(Prestamos, id=id)

    if request.method == 'POST':
        if prestamo.fecha_devolucion_real is not None:
            messages.warning(
                request,
                'Este préstamo ya tiene registrada la devolución.'
            )
        else:
            from django.utils import timezone

            prestamo.fecha_devolucion_real = timezone.localdate()
            prestamo.save(update_fields=['fecha_devolucion_real'])

            actualizar_disponibilidad_libro(prestamo.libro)

            messages.success(
                request,
                'Devolución registrada con éxito.'
            )

        return redirect('prestamos')

    return render(
        request,
        'Administrador/registrar_devolucion.html',
        {'prestamo': prestamo}
    )

