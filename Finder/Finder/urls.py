from django.contrib import admin
from django.urls import path
from mifinder import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name ='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('mi-perfil/', views.perfil, name='mi_perfil'),
    path('mi-perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('report', views.report_pet, name='report_pet'),
    path('registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    path('actualizar-imagen-perfil/', views.actualizar_imagen_perfil, name='actualizar_imagen_perfil'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
