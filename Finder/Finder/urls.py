from django.contrib import admin
from django.urls import path
from mifinder import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name ='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
]
