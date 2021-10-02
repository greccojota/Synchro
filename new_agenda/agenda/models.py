from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
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
        return self.dt_evento.strftime('%d/%m/%Y %H:%M Hrs')

    def get_data_input_evento(self):
        return self.dt_evento.strftime('%Y-%m-%dT%H:%M')

    def get_evento_atrasado(self):
        #if datetime.fromisoformat(self.dt_evento.strftime('%Y-%m-%d %H:%M:%S')) < datetime.now():
        if self.dt_evento < datetime.now():
            return True
        else:
            return False

    def get_evento_30min(self):
        #diferenca = datetime.fromisoformat(self.dt_evento.strftime('%Y-%m-%d %H:%M:%S')) - datetime.now()
        diferenca = self.dt_evento - datetime.now()
        if diferenca <= timedelta(hours=1):
            return True
        else:
            return False