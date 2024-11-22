from django.conf import settings
import os
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.http import JsonResponse
import cv2
from django.core.files.storage import default_storage
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import torch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from torchvision import models, transforms
import hashlib
import time
# Cargar el modelo ResNet50 preentrenado y remover la última capa
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))  # Remover la capa de clasificación final
model.eval()

# Transformación para extraer características
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Aumentaciones para simular condiciones de rotación y cambios de brillo
augmentation_transforms = [
    transforms.RandomRotation(degrees=[-30, 30]),  # Rotación entre -30 y 30 grados
    transforms.ColorJitter(brightness=0.3),         # Variación en brillo
]

def index_view(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        # Buscar el correo en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario, contrasena FROM usuario WHERE correo = %s", [correo])
            user = cursor.fetchone()  # user será una tupla con (id_usuario, contrasena) o None
        
        if user:
            print("Contraseña ingresada:", contrasena)
            print("Hash de la contraseña en la BD:", user[1])
            # Validar la contraseña con check_password
            if check_password(contrasena, user[1]):  # user[1] es la contraseña hasheada en la BD
                # Iniciar sesión y redirigir al home
                request.session['user_id'] = user[0]  # Guardar el ID del usuario en la sesión
                return redirect('home')  # Redirigir al home si el login es exitoso
            else:
                messages.error(request, 'La contraseña es incorrecta')
        else:
            messages.error(request, 'El correo no está registrado')

    return render(request, 'login.html')
    # Elimina los mensajes irrelevantes antes de cargar la vista de login
    storage = messages.get_messages(request)
    storage.used = True  # Marcar todos los mensajes como consumidos

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = make_password(request.POST.get('contrasena'))  # Hashear la contraseña
        telefono = request.POST.get('telefono')

        # Verificar si el correo ya está registrado
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuario WHERE correo = %s", [correo])
            existing_user = cursor.fetchone()  # Si encuentra algo, devuelve una tupla

        if existing_user:
            # Si el correo ya está registrado, muestra un mensaje de error
            messages.error(request, "El correo ya está registrado. Por favor, usa otro.")
            return redirect('register')

        # Si el correo no está registrado, proceder con la inserción
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuario (nombre, correo, contrasena, fecha_registro, telefono)
                VALUES (%s, %s, %s, NOW(), %s)
            """, [nombre, correo, contrasena, telefono])

        messages.success(request, "Registro completado con éxito.")
        return redirect('login')

    return render(request, 'register.html')


def home_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    print("ID del usuario autenticado:", user_id)

    # Consultar las mascotas registradas por el usuario
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_mascota, nombre FROM mascota WHERE id_usuario = %s", [user_id])
        mascotas = cursor.fetchall()

    # Convertir el resultado de la consulta a un diccionario para la plantilla
    mascotas = [{'id_mascota': m[0], 'nombre': m[1]} for m in mascotas]

    # Renderizar la vista de home con las mascotas del usuario
    return render(request, 'home.html', {'mascotas': mascotas})

def actualizar_contrasenas():
    # Seleccionar todos los usuarios con contraseñas en texto plano
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_usuario, contrasena FROM usuario")
        usuarios = cursor.fetchall()
    
    for usuario in usuarios:
        id_usuario, contrasena_texto_plano = usuario
        contrasena_hasheada = make_password(contrasena_texto_plano)
        
        # Actualizar la contraseña en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario
                SET contrasena = %s
                WHERE id_usuario = %s
            """, [contrasena_hasheada, id_usuario])
# Vista para 'Mi perfil'
def perfil(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    # Buscar los datos del usuario
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, correo, telefono, imagen_perfil FROM usuario WHERE id_usuario = %s", [user_id])
        usuario = cursor.fetchone()

    if not usuario:
        return redirect('login')

    # Consultar las mascotas registradas por el usuario
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, raza, color, edad, descripcion, imagen FROM mascota WHERE id_usuario = %s", [user_id])
        mascotas = cursor.fetchall()

    # Procesar las mascotas en un formato adecuado para la plantilla
    mascotas = [
        {
            'nombre': m[0],
            'raza': m[1],
            'color': m[2],
            'edad': m[3],
            'descripcion': m[4],
            'imagen': m[5] if m[5] else '/path/to/default/image.jpg'  # Imagen por defecto si no hay ninguna
        } for m in mascotas
    ]
    
    # Consultar los reportes realizados por el usuario
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.titulo, p.descripcion, p.fecha_publicacion, m.nombre, g.latitud, g.longitud, p.imagen
            FROM publicacion p
            JOIN mascota m ON p.id_mascota = m.id_mascota
            JOIN geolocalizacion g ON p.id_geolocalizacion = g.id_geolocalizacion
            WHERE p.id_usuario = %s
        """, [user_id])
        reportes = cursor.fetchall()

    # Procesar los reportes en un formato adecuado para la plantilla
    reportes = [
        {
            'titulo': r[0],
            'descripcion': r[1],
            'fecha': r[2],
            'nombre_mascota': r[3],
            'latitud': r[4],
            'longitud': r[5],
            'imagen': r[6] if r[6] else '/path/to/default/image.jpg'  # Imagen por defecto si no hay ninguna
        } for r in reportes
    ]

    # Procesar la ruta de la imagen de perfil
    imagen_perfil = usuario[3] if usuario[3] else '/path/to/default/image.jpg'  # Ruta a la imagen por defecto si no hay ninguna

    return render(request, 'mi_perfil.html', {
        'usuario': {
            'nombre': usuario[0],
            'correo': usuario[1],
            'telefono': usuario[2],
            'imagen_perfil': imagen_perfil  # Pasar la ruta de la imagen de perfil
        },
        'mascotas': mascotas,
        'reportes': reportes
    })

def actualizar_imagen_perfil(request):
    if request.method == 'POST':
        imagen_perfil = request.FILES.get('imagen_perfil')
        user_id = request.session.get('user_id')

        if imagen_perfil:
            # Guardar el archivo de imagen en el sistema de archivos
            fs = FileSystemStorage()
            filename = fs.save(imagen_perfil.name, imagen_perfil)
            file_url = fs.url(filename)

            # Actualizar la base de datos con la ruta de la imagen
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuario
                    SET imagen_perfil = %s
                    WHERE id_usuario = %s
                """, [file_url, user_id])

        return redirect('mi_perfil')

    return redirect('mi_perfil')


    
# Vista para editar el perfil
def editar_perfil(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    # Si el método es POST, se están enviando datos desde el formulario
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        # Actualizar la base de datos con los nuevos datos del perfil
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario 
                SET nombre = %s, correo = %s, telefono = %s
                WHERE id_usuario = %s
            """, [nombre, correo, telefono, user_id])

        messages.success(request, "Perfil actualizado con éxito.")
        return redirect('mi_perfil')  # Redirigir de vuelta al perfil después de actualizar

    # Si el método es GET, se cargan los datos actuales del usuario para mostrarlos en el formulario
    else:
        # Obtener los datos del usuario actual
        with connection.cursor() as cursor:
            cursor.execute("SELECT nombre, correo, telefono FROM usuario WHERE id_usuario = %s", [user_id])
            usuario = cursor.fetchone()

        if not usuario:
            return redirect('login')

        # Pasar los datos del usuario al formulario
        return render(request, 'editar_perfil.html', {
            'usuario': {
                'nombre': usuario[0],
                'correo': usuario[1],
                'telefono': usuario[2]
            }
        })



def report_pet(request):
    if request.method == 'POST':
        # Lógica para guardar el reporte de la mascota perdida
        name = request.POST.get('name')
        description = request.POST.get('description')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        # Aquí puedes agregar lógica para guardar estos datos en la base de datos
        # Redirige a la página principal después de enviar el reporte
        return redirect('home')
        


def registrar_mascota(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        raza = request.POST.get('raza')
        color = request.POST.get('color')
        edad = request.POST.get('edad')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')
        user_id = request.session.get('user_id')

        if not user_id:
            messages.error(request, "Debes estar logueado para registrar una mascota.")
            return redirect('login')

        # Guardar la imagen en la carpeta 'mis_mascotas'
        imagen_url = None
        if imagen:
            # Define la subcarpeta
            upload_folder = os.path.join(settings.MEDIA_ROOT, 'mis_mascotas')
            os.makedirs(upload_folder, exist_ok=True)  # Crear la carpeta si no existe

            # Guardar el archivo en la carpeta específica
            file_path = os.path.join(upload_folder, imagen.name)
            with open(file_path, 'wb+') as destination:
                for chunk in imagen.chunks():
                    destination.write(chunk)
            
            # Generar la URL para almacenar en la base de datos
            imagen_url = f"/media/mis_mascotas/{imagen.name}"

        # Guardar la mascota en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO mascota (id_usuario, nombre, raza, color, edad, descripcion, imagen)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [user_id, nombre, raza, color, edad, descripcion, imagen_url])

        messages.success(request, "Mascota registrada con éxito.")
        return redirect('mi_perfil')  # Redirigir a la misma página

    return render(request, 'registrar_mascota.html')



@csrf_exempt
def report_pet(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        report_date = request.POST.get('reportDate')
        location = request.POST.get('location')
        photo = request.FILES.get('photo')
        id_mascota = request.POST.get('id_mascota')  # Obtener el ID de la mascota seleccionada

        try:
            # Procesar la latitud y longitud
            lat, lng = location.replace('Lat: ', '').replace('Lng: ', '').split(', ')
            
            # Guardar la geolocalización y obtener el id
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO geolocalizacion (latitud, longitud) VALUES (%s, %s) RETURNING id_geolocalizacion",
                    [lat, lng]
                )
                id_geolocalizacion = cursor.fetchone()[0]

            # Guardar el archivo de imagen (si está presente)
            if photo:
                fs = FileSystemStorage()
                filename = fs.save(photo.name, photo)
                photo_url = fs.url(filename)
            else:
                photo_url = None  # O una URL por defecto si no se sube imagen

            # Guardar el reporte de la mascota
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO publicacion (
                        id_usuario, titulo, descripcion, fecha_publicacion, 
                        id_mascota, id_geolocalizacion, imagen, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    request.session.get('user_id'),
                    'Reporte de mascota perdida',
                    description,
                    report_date,
                    id_mascota,
                    id_geolocalizacion,
                    photo_url,  # Guardar la URL de la imagen
                    'activa'
                ])

            return JsonResponse({'success': True})

        except Exception as e:
            # Imprimir el error para debug
            print(f'Error al guardar el reporte: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


def obtener_reportes(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id_publicacion, p.titulo, p.descripcion, p.fecha_publicacion, m.nombre, g.latitud, g.longitud, p.imagen, u.nombre, u.telefono
            FROM publicacion p
            JOIN mascota m ON p.id_mascota = m.id_mascota
            JOIN geolocalizacion g ON p.id_geolocalizacion = g.id_geolocalizacion
            JOIN usuario u ON p.id_usuario = u.id_usuario
            WHERE p.estado = 'activa'
        """)
        reportes = cursor.fetchall()
    
    # Formatear los datos para enviarlos en formato JSON
    reportes_json = [
        {
            'id': r[0],  # Incluye el ID del reporte aquí
            'titulo': r[1],
            'descripcion': r[2],
            'fecha': r[3].strftime("%Y-%m-%d %H:%M:%S"),
            'nombre_mascota': r[4],
            'latitud': float(r[5]),
            'longitud': float(r[6]),
            'imagen': r[7],
            'nombre_usuario': r[8],
            'telefono_usuario': r[9]
        } for r in reportes
    ]
    
    return JsonResponse(reportes_json, safe=False)

def obtener_embeddings_con_augmentacion(imagen_path):
    """Extrae un embedding robusto aplicando rotaciones y cambios de brillo."""
    imagen = Image.open(imagen_path).convert("RGB")
    embeddings = []

    # Extraer embeddings con y sin augmentación
    for augment in augmentation_transforms + [None]:  # Incluye la versión original sin augmentación
        if augment:
            augmented_image = augment(imagen)
        else:
            augmented_image = imagen

        transformed_image = transform(augmented_image).unsqueeze(0)
        with torch.no_grad():
            embedding = model(transformed_image).flatten()
        embeddings.append(embedding.numpy())

    # Promediar los embeddings obtenidos para obtener un embedding rotacionalmente invariante
    promedio_embedding = np.mean(embeddings, axis=0)
    return promedio_embedding

def calcular_similitud_resnet(imagen1_path, imagen2_path):
    """Calcula la similitud entre dos imágenes usando embeddings de ResNet con augmentación."""
    embedding1 = obtener_embeddings_con_augmentacion(imagen1_path)
    embedding2 = obtener_embeddings_con_augmentacion(imagen2_path)

    # Calcular la similitud de coseno entre los embeddings
    embedding1 = embedding1.reshape(1, -1)
    embedding2 = embedding2.reshape(1, -1)
    similitud = cosine_similarity(embedding1, embedding2)[0][0]
    return similitud * 100  # Convertir a porcentaje

@csrf_exempt
def crear_comentario(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        id_publicacion = request.POST.get('id_publicacion')
        id_usuario = request.session.get('user_id')
        imagen = request.FILES.get('imagen')

        if not id_usuario:
            return JsonResponse({'mensaje': 'Debe iniciar sesión para comentar'}, status=403)

        if not id_publicacion:
            return JsonResponse({'mensaje': 'ID de publicación no encontrado'}, status=400)

        imagen_url = None
        similitud_suficiente = False
        similitud = 0

        if imagen:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'comentarios'))
            filename = fs.save(imagen.name, imagen)
            imagen_url = '/media/comentarios/' + filename

            # Obtener la imagen del reporte para comparar
            with connection.cursor() as cursor:
                cursor.execute("SELECT imagen FROM publicacion WHERE id_publicacion = %s", [id_publicacion])
                publicacion = cursor.fetchone()

            if publicacion and publicacion[0]:
                ruta_imagen_reporte = os.path.join(settings.BASE_DIR, publicacion[0].replace('/media/', 'media/'))
                ruta_imagen_comentario = os.path.join(settings.MEDIA_ROOT, 'comentarios', filename)

                # Calcular la similitud usando ResNet con augmentación
                similitud = calcular_similitud_resnet(ruta_imagen_reporte, ruta_imagen_comentario)
                similitud_suficiente = similitud >= 75  # Cambiado a 75%
                print(f"Similitud suficiente: {similitud_suficiente} con {similitud:.2f}% de similitud")

        # Guardar el comentario en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO comentario (id_publicacion, id_usuario, contenido, fecha_comentario, imagen)
                VALUES (%s, %s, %s, NOW(), %s)
            """, [id_publicacion, id_usuario, contenido, imagen_url])

        # Crear una notificación si la similitud es suficiente
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM publicacion WHERE id_publicacion = %s", [id_publicacion])
            owner_id = cursor.fetchone()[0]

        if owner_id and id_usuario != owner_id:
            if similitud_suficiente:
                crear_notificacion(
                    owner_id,
                    f"Se ha encontrado una mascota con un {similitud:.2f}% de similitud.",
                    id_publicacion=id_publicacion
                )
                print("Notificación de imagen similar creada.")
            else:
                crear_notificacion(
                    owner_id,
                    "Nuevo comentario en tu publicación.",
                    id_publicacion=id_publicacion
                )
                print("Notificación de nuevo comentario creada.")

        return JsonResponse({'mensaje': 'Comentario añadido correctamente'})

    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)



def obtener_comentarios(request, report_id):
    # Supongamos que tienes un modelo o una consulta para obtener los comentarios
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.contenido, c.imagen, c.fecha_comentario, u.nombre AS usuario
            FROM comentario c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            WHERE c.id_publicacion = %s
            ORDER BY c.fecha_comentario DESC
        """, [report_id])
        comentarios = cursor.fetchall()

    # Formatear los resultados en un diccionario para JSON
    comentarios_json = [
        {
            'contenido': comentario[0],
            'imagen': comentario[1],
            'fecha': comentario[2].strftime("%Y-%m-%d %H:%M:%S"),
            'usuario': comentario[3],
        }
        for comentario in comentarios
    ]

    return JsonResponse(comentarios_json, safe=False)

def crear_notificacion(user_id, mensaje, estado='no leída', id_publicacion=None):
    """Crea una notificación en la base de datos."""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO notificacion (id_usuario, mensaje, fecha_notificacion, estado, id_publicacion)
            VALUES (%s, %s, NOW(), %s, %s)
        """, [user_id, mensaje, estado, id_publicacion])


def ver_notificaciones(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    print("ID del usuario autenticado:", user_id)

    # Consultar las notificaciones del usuario
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT mensaje, fecha_notificacion, estado, id_publicacion
            FROM notificacion
            WHERE id_usuario = %s
            ORDER BY fecha_notificacion DESC
        """, [user_id])
        notificaciones_raw = cursor.fetchall()

    # Procesar los resultados para la plantilla
    notificaciones = [
        {
            'message': n[0],
            'created_at': n[1],
            'estado': n[2],
            'reporte_id': n[3]  # Incluye el reporte_id
        } for n in notificaciones_raw
    ]

    return render(request, 'notificaciones.html', {'notificaciones': notificaciones})
    
@require_POST
def marcar_notificacion_leida(request, id):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=403)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE notificacion 
            SET estado = 'leída' 
            WHERE id_publicacion = %s AND id_usuario = %s
        """, [id, user_id])
    
    return JsonResponse({'success': True})
