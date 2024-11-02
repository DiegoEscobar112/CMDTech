# mifinder/context_processors.py

from django.db import connection

def user_notifications_count(request):
    if request.user.is_authenticated and 'user_id' in request.session:
        user_id = request.session['user_id']
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM notificacion WHERE id_usuario = %s AND estado = 'no leída'", [user_id])
            count = cursor.fetchone()[0]
        print("Número de notificaciones no leídas:", count)  # Esto imprimirá el conteo en la consola
        return {'user_notifications_count': count}
    return {'user_notifications_count': 0}
