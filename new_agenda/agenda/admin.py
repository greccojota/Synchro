from django.contrib import admin
from agenda.models import Evento
# Register your models here.

class EventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'dt_evento', 'dt_criacao', 'local')
    list_filter = ('titulo','usuario','dt_evento',)

admin.site.register(Evento, EventoAdmin)