from django import forms
from django.db import models
from .models import Usuarios, Libros, Prestamos

class CrearUsuariosForm(forms.ModelForm):
    """
    Formulario para la creación de usuarios basado en el modelo Usuarios.
    """

    class Meta:
        model = Usuarios
        fields = ['nombre_usuario', 'email_usuario']

        labels = {
            'nombre_usuario': 'Nombre de Usuario',
            'email_usuario': 'Correo Electrónico',
        }

        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),

            'email_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
        }


class CrearLibrosForm(forms.ModelForm):
    """
    Formulario para la creación de libros basado en el modelo Libros.
    """

    class Meta:
        model = Libros
        fields = [
    'titulo_libro',
    'autor',
    'anio',
    'genero_categoria',
    'editorial',
    'isbn',
    'disponibilidad'
]

        labels = {
    'titulo_libro': 'Título del Libro',
    'autor': 'Autor',
    'anio': 'Año',
    'genero_categoria': 'Género / Categoría',
    'editorial': 'Editorial',
    'isbn': 'ISBN',
    'disponibilidad': 'Disponibilidad',
}

        widgets = {
    'titulo_libro': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. Don Quijote de la Mancha'
    }),

    'autor': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. Miguel de Cervantes'
    }),

    'anio': forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. 1605'
    }),

    'genero_categoria': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. Literatura clásica'
    }),

    'editorial': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. Editorial Planeta'
    }),

    'isbn': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej. 978-950-04-1234-5'
    }),

    'disponibilidad': forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }),
}

        

class CrearPrestamosForm(forms.ModelForm):
    """
    Formulario para registrar y editar préstamos.
    Solo permite seleccionar libros disponibles
    y conserva el libro del préstamo actual al editar.
    """

    class Meta:
        model = Prestamos
        fields = [
            'usuario',
            'libro',
            'fecha_prestamo',
            'fecha_devolucion_prevista',
        ]

        labels = {
            'usuario': 'Usuario',
            'libro': 'Libro',
            'fecha_prestamo': 'Fecha del Préstamo',
            'fecha_devolucion_prevista': 'Fecha Prevista de Devolución',
        }

        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-control'
            }),

            'libro': forms.Select(attrs={
                'class': 'form-control'
            }),

            'fecha_prestamo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'fecha_devolucion_prevista': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        libros_disponibles = Libros.objects.filter(
            disponibilidad=True
        )

        if self.instance and self.instance.pk:
            libros_disponibles = (
                libros_disponibles
                | Libros.objects.filter(
                    pk=self.instance.libro_id
                )
            )

        self.fields['libro'].queryset = (
            libros_disponibles.distinct()
        )

    
    def clean(self):
        datos = super().clean()

        fecha_prestamo = datos.get('fecha_prestamo')
        fecha_prevista = datos.get('fecha_devolucion_prevista')

        if fecha_prestamo and fecha_prevista:
            if fecha_prevista < fecha_prestamo:
                mensaje = (
                    'La fecha prevista de devolución no puede '
                    'ser anterior a la fecha del préstamo.'
                )

                self.add_error('fecha_devolucion_prevista', mensaje)
                self.add_error(None, f'ERROR DE FECHAS: {mensaje}')
        return datos
