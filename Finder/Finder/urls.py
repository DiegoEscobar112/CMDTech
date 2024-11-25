from django.contrib import admin
from django.urls import path
from mifinder import views
from django.conf.urls.static import static
from django.conf import settings
from mifinder.views import actualizar_imagen_perfil


urlpatterns = [
    path('report-pet/', views.report_pet, name='report_pet'),
    path('admin/', admin.site.urls),
    path('', views.index_view, name ='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('mi-perfil/', views.perfil, name='mi_perfil'),
    path('mi-perfil/editar/', views.editar_perfil, name='editar_perfil'),
    #path('report', views.report_pet, name='report_pet'),
    path('registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    path('actualizar-imagen-perfil/', views.actualizar_imagen_perfil, name='actualizar_imagen_perfil'),
    path('obtener_reportes/', views.obtener_reportes, name='obtener_reportes'),
    path('crear-comentario/', views.crear_comentario, name='crear_comentario'),
    path('obtener_comentarios/<int:report_id>/', views.obtener_comentarios, name='obtener_comentarios'),
    path('notificaciones/', views.ver_notificaciones, name='ver_notificaciones'),
    path('marcar_notificacion_leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('marcar_notificacion_leida/<int:id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    #appmovil
    path('api/actualizar-imagen-perfil/', views.actualizar_imagen_perfil, name='actualizar_imagen_perfil'),
    path('api/obtener-mascotas-usuario/', views.obtener_mascotas_usuario, name='obtener_mascotas_usuario'),
    path('api/obtener-reportes-usuario/', views.obtener_reportes_usuario, name='obtener_reportes_usuario'),
    path('api/report-pet/', views.report_pet, name='report_pet'),  # Ajuste asegurado
    path('api/obtener-reportes/', views.obtener_reportes, name='obtener_reportes'),
    path('api/obtener_comentarios/<int:report_id>/', views.obtener_comentarios, name='obtener_comentarios'),
    path('api/crear-comentario/', views.crear_comentario, name='crear_comentario'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
