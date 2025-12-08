from django.db import models

class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/')
    contenido_original = models.TextField()
    resumen = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo