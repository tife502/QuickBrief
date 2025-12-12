from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
from transformers import pipeline
from .models import Documento
import logging
import traceback

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def subir_documento(request):
    try:
        print("FILES:", request.FILES)
        print("POST:", request.POST)
        
        titulo = request.POST.get('titulo')
        archivo = request.FILES.get('archivo')
        
        if not titulo or not archivo:
            return JsonResponse({'error': 'Título y archivo son requeridos'}, status=400)
        
        # Extraer texto del PDF
        reader = PdfReader(archivo)
        texto = ''.join([page.extract_text() for page in reader.pages])
        
        # Generar resumen
        resumidor = pipeline("summarization", model="facebook/bart-large-cnn")
        resumen_obj = resumidor(texto[:1024], max_length=150, min_length=50)
        resumen = resumen_obj[0]['summary_text']
        
        # Guardar en BD
        doc = Documento.objects.create(
            titulo=titulo,
            archivo=archivo,
            contenido_original=texto,
            resumen=resumen
        )
        
        return JsonResponse({
            'id': doc.id,
            'titulo': doc.titulo,
            'resumen': doc.resumen,
            'fecha_creacion': doc.fecha_creacion.isoformat()
        }, status=201)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e), 'detail': traceback.format_exc()}, status=500)

@require_http_methods(["GET"])
def ver_documento(request, pk):
    try:
        doc = Documento.objects.get(pk=pk)
        return JsonResponse({
            'id': doc.id,
            'titulo': doc.titulo,
            'resumen': doc.resumen,
            'contenido_original': doc.contenido_original,
            'fecha_creacion': doc.fecha_creacion.isoformat()
        })
    except Documento.DoesNotExist:
        return JsonResponse({'error': 'Documento no encontrado'}, status=404)

@require_http_methods(["GET"])
def listar_documentos(request):
    try:
        documentos = Documento.objects.all().order_by('-fecha_creacion')
        data = [
            {
                'id': doc.id,
                'titulo': doc.titulo,
                'resumen': doc.resumen,
                'fecha_creacion': doc.fecha_creacion.isoformat()
            }
            for doc in documentos
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)