from django.shortcuts import render

# Create your views here.
def pagina_inicio(request):
    return render (request, 'inicio/inicio.html')