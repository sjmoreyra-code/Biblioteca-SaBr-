from django.contrib import admin
from .models import Usuarios, Libros


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    search_fields = ['nombre_usuario', 'email_usuario']


admin.site.register(Libros)
