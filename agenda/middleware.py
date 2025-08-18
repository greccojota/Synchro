from django.utils.deprecation import MiddlewareMixin
from .models import PerfilUsuario

class PerfilUsuarioMiddleware(MiddlewareMixin):
    """
    Middleware para garantir que todo usuário autenticado tenha um perfil.
    Cria automaticamente o perfil se não existir.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_anonymous:
            # Verificar se o usuário tem perfil
            if not hasattr(request.user, 'perfil'):
                try:
                    # Tentar obter o perfil
                    perfil = PerfilUsuario.objects.get(usuario=request.user)
                    # Cache no objeto user para evitar queries desnecessárias
                    request.user._perfil = perfil
                except PerfilUsuario.DoesNotExist:
                    # Criar perfil se não existir
                    perfil = PerfilUsuario.objects.create(usuario=request.user)
                    request.user._perfil = perfil
        
        return None