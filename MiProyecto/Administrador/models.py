from django.db import models

# Create your models here.


class Usuarios(models.Model):
    nombre_usuario = models.CharField(max_length=30)
    email_usuario = models.EmailField()

    def __str__(self):
        return f'Nombre_usuario: {self.nombre_usuario}, Email_usuario: {self.email_usuario}'


class Libros(models.Model):
    titulo_libro = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    anio = models.IntegerField()
    genero_categoria = models.CharField(max_length=50)
    editorial = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, blank=True)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.titulo_libro} - {self.autor} ({self.anio})'



class Prestamos(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.PROTECT)
    libro = models.ForeignKey(Libros, on_delete=models.PROTECT)
    fecha_prestamo = models.DateField()

    # Campo antiguo: se conserva temporalmente para proteger los datos.
    fecha_devolucion = models.DateField(blank=True, null=True)

    # Nueva fecha límite para devolver el libro.
    fecha_devolucion_prevista = models.DateField(
        blank=True,
        null=True
    )

    # Se completa únicamente cuando el libro vuelve físicamente.
    fecha_devolucion_real = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.libro.titulo_libro} - {self.usuario.nombre_usuario}'



