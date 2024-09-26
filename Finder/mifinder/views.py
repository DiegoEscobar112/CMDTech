from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


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
        return redirect('login')  # Redirigir al login si no está autenticado
    return render(request, 'home.html')  # Mostrar la página home

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

