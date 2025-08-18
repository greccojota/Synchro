from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.validators import EmailValidator
import uuid
# Create your models here.

class Evento(models.Model):
    """Modelo principal para eventos da agenda"""
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta')
    ]
    
    titulo = models.CharField(max_length=100, verbose_name='Título')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    dt_evento = models.DateTimeField(verbose_name='Data do Evento')
    dt_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Criação')
    dt_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')
    categoria = models.ForeignKey('CategoriaEvento', on_delete=models.SET_NULL, blank=True, null=True, related_name='eventos')
    local = models.CharField(max_length=200, blank=True, null=True, verbose_name='Local')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default='media', verbose_name='Prioridade')
    concluido = models.BooleanField(default=False, verbose_name='Concluído')
    evento_dia_todo = models.BooleanField(default=False, verbose_name='Evento de dia inteiro')
    privado = models.BooleanField(default=True, verbose_name='Evento privado')
    cor_personalizada = models.CharField(max_length=7, blank=True, null=True, help_text='Cor em formato hex')

    class Meta:
        db_table = 'evento'

    def __str__(self):
        return self.titulo

    def get_data_evento(self):
        return self.dt_evento.strftime('%d/%m/%Y %H:%M Hrs')

    def get_data_input_evento(self):
        return self.dt_evento.strftime('%Y-%m-%dT%H:%M')

    def get_evento_atrasado(self):
        """Verifica se o evento está atrasado"""
        return self.dt_evento < timezone.now()

    def get_evento_30min(self):
        """Verifica se o evento está próximo (1 hora ou menos)"""
        diferenca = self.dt_evento - timezone.now()
        return diferenca <= timedelta(hours=1) and diferenca > timedelta(0)
    
    def get_cor_evento(self):
        """Retorna a cor do evento (personalizada ou da categoria)"""
        if self.cor_personalizada:
            return self.cor_personalizada
        if self.categoria:
            return self.categoria.cor
        return "#6366f1"  # Cor padrão
    
    def get_icone_evento(self):
        """Retorna o ícone do evento"""
        if self.categoria:
            return self.categoria.icone
        return "calendar"  # Ícone padrão
    
    def is_recorrente(self):
        """Verifica se o evento é recorrente"""
        return hasattr(self, 'recorrencia') and self.recorrencia is not None


class PerfilUsuario(models.Model):
    """Extensão do modelo User para informações adicionais"""
    PLANOS = [
        ('free', 'Gratuito'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial')
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=15, blank=True, null=True)
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    plano = models.CharField(max_length=20, choices=PLANOS, default='free')
    data_assinatura = models.DateTimeField(blank=True, null=True)
    limite_eventos_mes = models.IntegerField(default=10)
    email_verificado = models.BooleanField(default=False)
    token_verificacao = models.UUIDField(default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    def eventos_criados_mes(self):
        """Conta eventos criados no mês atual"""
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return Evento.objects.filter(
            usuario=self.usuario,
            dt_criacao__gte=inicio_mes
        ).count()
    
    def pode_criar_evento(self):
        """Verifica se pode criar mais eventos baseado no plano"""
        if self.plano != 'free':
            return True
        return self.eventos_criados_mes() < self.limite_eventos_mes


class CategoriaEvento(models.Model):
    """Categorias para organizar eventos"""
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=7, default="#6366f1")  # Hex color
    icone = models.CharField(max_length=50, default="calendar")
    descricao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categorias')
    ativo = models.BooleanField(default=True)
    dt_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoria de Evento"
        verbose_name_plural = "Categorias de Eventos"
        unique_together = ['nome', 'usuario']
    
    def __str__(self):
        return f"{self.nome} ({self.usuario.username})"


class EventoRecorrente(models.Model):
    """Configuração para eventos que se repetem"""
    TIPOS_RECORRENCIA = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('yearly', 'Anual')
    ]
    
    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ]
    
    evento_base = models.OneToOneField(Evento, on_delete=models.CASCADE, related_name='recorrencia')
    tipo = models.CharField(max_length=10, choices=TIPOS_RECORRENCIA)
    intervalo = models.IntegerField(default=1, help_text="A cada X dias/semanas/meses/anos")
    dias_semana = models.JSONField(blank=True, null=True, help_text="Para recorrência semanal")
    dia_mes = models.IntegerField(blank=True, null=True, help_text="Para recorrência mensal")
    data_fim = models.DateField(blank=True, null=True)
    max_ocorrencias = models.IntegerField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Recorrência {self.get_tipo_display()} - {self.evento_base.titulo}"
    
    def gerar_proximas_ocorrencias(self, limite=50):
        """Gera as próximas ocorrências do evento"""
        ocorrencias = []
        data_atual = self.evento_base.dt_evento
        contador = 0
        
        while contador < limite:
            if self.data_fim and data_atual.date() > self.data_fim:
                break
            if self.max_ocorrencias and contador >= self.max_ocorrencias:
                break
                
            if data_atual > timezone.now():
                ocorrencias.append(data_atual)
            
            # Calcular próxima data baseado no tipo
            if self.tipo == 'daily':
                data_atual += timedelta(days=self.intervalo)
            elif self.tipo == 'weekly':
                data_atual += timedelta(weeks=self.intervalo)
            elif self.tipo == 'monthly':
                # Adicionar meses (simplificado)
                mes = data_atual.month + self.intervalo
                ano = data_atual.year
                while mes > 12:
                    mes -= 12
                    ano += 1
                data_atual = data_atual.replace(year=ano, month=mes)
            elif self.tipo == 'yearly':
                data_atual = data_atual.replace(year=data_atual.year + self.intervalo)
            
            contador += 1
        
        return ocorrencias


class NotificacaoEvento(models.Model):
    """Sistema de notificações para eventos"""
    TIPOS_NOTIFICACAO = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification')
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=10, choices=TIPOS_NOTIFICACAO, default='email')
    tempo_antecedencia = models.IntegerField(help_text="Minutos antes do evento")
    mensagem_customizada = models.TextField(blank=True, null=True)
    enviado = models.BooleanField(default=False)
    data_envio = models.DateTimeField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Notificação de Evento"
        verbose_name_plural = "Notificações de Eventos"
    
    def __str__(self):
        return f"Notificação {self.get_tipo_display()} - {self.evento.titulo}"