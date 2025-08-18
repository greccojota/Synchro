from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Agenda principal
    path('', views.lista_eventos, name='lista'),
    
    # Eventos
    path('evento/', views.evento, name='evento'),
    path('evento/submit/', views.submit_evento, name='submit_evento'),
    path('evento/delete/<int:id_evento>/', views.delete_evento, name='delete_evento'),
    
    # Histórico
    path('historico/', views.historico_eventos, name='historico'),
    path('historico/evento/delete/<int:id_evento>/', views.delete_evento, name='delete_evento_historico'),
    
    # Categorias
    path('categorias/', views.categorias_evento, name='categorias'),
    path('categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/deletar/<int:categoria_id>/', views.deletar_categoria, name='deletar_categoria'),
    
    # Perfil
    path('perfil/', views.perfil_usuario, name='perfil'),
    
    # API
    path('api/eventos/<int:id_usuario>/', views.json_lista_evento, name='api_eventos'),
]