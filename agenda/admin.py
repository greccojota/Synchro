from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'dt_evento', 'local', 'dt_criacao')
    list_filter = ('dt_evento', 'dt_criacao', 'usuario')
    search_fields = ('titulo', 'descricao', 'local', 'usuario__username')
    ordering = ('-dt_evento',)
    date_hierarchy = 'dt_evento'
    list_per_page = 20
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'usuario')
        }),
        ('Data e Local', {
            'fields': ('dt_evento', 'local')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)