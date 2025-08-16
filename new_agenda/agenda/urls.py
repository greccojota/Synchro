from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Agenda principal
    path('', views.lista_eventos, name='lista'),
    
    # Eventos
    path('evento/', views.evento, name='evento'),
    path('evento/submit/', views.submit_evento, name='submit_evento'),
    path('evento/delete/<int:id_evento>/', views.delete_evento, name='delete_evento'),
    
    # Histórico
    path('historico/', views.historico_eventos, name='historico'),
    path('historico/evento/delete/<int:id_evento>/', views.delete_evento, name='delete_evento_historico'),
    
    # API
    path('api/eventos/<int:id_usuario>/', views.json_lista_evento, name='api_eventos'),
]