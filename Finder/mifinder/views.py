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
        cursor.execute("SELECT nombre, raza, color, edad, descripcion FROM mascota WHERE id_usuario = %s", [user_id])
        mascotas = cursor.fetchall()

    # Consultar los reportes realizados por el usuario
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.titulo, p.descripcion, p.fecha_publicacion, m.nombre, g.latitud, g.longitud 
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
            'longitud': r[5]
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
        user_id = request.session.get('user_id')

        if not user_id:
            messages.error(request, "Debes estar logueado para registrar una mascota.")
            return redirect('login')

        # Guardar la mascota en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO mascota (id_usuario, nombre, raza, color, edad, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [user_id, nombre, raza, color, edad, descripcion])

        # Mostrar un mensaje de éxito
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
            SELECT p.titulo, p.descripcion, p.fecha_publicacion, m.nombre, g.latitud, g.longitud, p.imagen, u.nombre, u.telefono
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
            'titulo': r[0],
            'descripcion': r[1],
            'fecha': r[2].strftime("%Y-%m-%d %H:%M:%S"),
            'nombre_mascota': r[3],
            'latitud': float(r[4]),
            'longitud': float(r[5]),
            'imagen': r[6],
            'nombre_usuario': r[7],
            'telefono_usuario': r[8]
        } for r in reportes
    ]
    
    return JsonResponse(reportes_json, safe=False)

