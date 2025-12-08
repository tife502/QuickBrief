from django.shortcuts import render, redirect
from PyPDF2 import PdfReader
from transformers import pipeline
from .models import Documento
from .forms import DocumentoForm

def subir_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            
            # Extraer texto del PDF
            pdf_file = request.FILES['archivo']
            reader = PdfReader(pdf_file)
            texto = ''.join([page.extract_text() for page in reader.pages])
            doc.contenido_original = texto
            
            # Generar resumen con Hugging Face
            resumidor = pipeline("summarization", model="facebook/bart-large-cnn")
            resumen = resumidor(texto[:1024], max_length=150, min_length=50)
            doc.resumen = resumen[0]['summary_text']
            
            doc.save()
            return redirect('ver_documento', pk=doc.pk)
    else:
        form = DocumentoForm()
    
    return render(request, 'resumidor/subir.html', {'form': form})

def ver_documento(request, pk):
    doc = Documento.objects.get(pk=pk)
    return render(request, 'resumidor/detalle.html', {'documento': doc})