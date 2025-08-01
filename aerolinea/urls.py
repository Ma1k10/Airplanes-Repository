from django.contrib import admin
from django.urls import path
from usuarios import views as user_views
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('', views.home, name='home'),  # Asegurate de tener una vista 'home'
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('aviones/crear/', views.crear_avion, name='crear_avion'),
    path('aviones/', views.lista_aviones, name='lista_aviones'),
    path('aviones/crear/', views.crear_avion, name='crear_avion'),
]
