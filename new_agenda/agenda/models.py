from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import pytz
# Create your models here.

class Evento(models.Model):
    titulo = models.CharField(max_length=100) # parametro que determina o máximo de caracter que o campo pode ter;
    descricao = models.TextField(blank=True, null=True) #esses doi parametros permitem que o campo seja nulo, ou seja, não é obrigatório preechelo;
    dt_evento = models.DateTimeField(verbose_name='Data do Evento')
    dt_criacao = models.DateTimeField(auto_now=True, verbose_name='Data da Criação') #auto_now > sempre que um registro for criado, será criado com a data atual;
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    local = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'evento'

    def __str__(self):
        return self.titulo

    def get_data_evento(self):
        """Retorna data formatada no timezone local"""
        br_timezone = pytz.timezone('America/Sao_Paulo')
        dt_local = self.dt_evento.astimezone(br_timezone)
        return dt_local.strftime('%d/%m/%Y %H:%M Hrs')

    def get_data_input_evento(self):
        """Retorna data no formato HTML datetime-local no timezone local"""
        br_timezone = pytz.timezone('America/Sao_Paulo')
        dt_local = self.dt_evento.astimezone(br_timezone)
        return dt_local.strftime('%Y-%m-%dT%H:%M')

    def get_evento_atrasado(self):
        """Verifica se o evento está atrasado usando timezone-aware datetime"""
        return self.dt_evento < timezone.now()

    def get_evento_30min(self):
        """Verifica se o evento está próximo (dentro de 1 hora)"""
        diferenca = self.dt_evento - timezone.now()
        return diferenca <= timedelta(hours=1) and diferenca > timedelta(0)