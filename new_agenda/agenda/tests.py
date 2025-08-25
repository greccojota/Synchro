from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from .models import Evento


class EventoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.evento = Evento.objects.create(
            titulo='Evento Teste',
            descricao='Descrição do evento teste',
            dt_evento=timezone.now() + timedelta(hours=2),
            usuario=self.user,
            local='Local Teste'
        )

    def test_evento_creation(self):
        """Testa se o evento foi criado corretamente"""
        self.assertEqual(self.evento.titulo, 'Evento Teste')
        self.assertEqual(self.evento.usuario, self.user)
        self.assertEqual(str(self.evento), 'Evento Teste')

    def test_evento_atrasado(self):
        """Testa se evento no futuro não está atrasado"""
        self.assertFalse(self.evento.get_evento_atrasado())
        
        # Testa evento no passado
        evento_passado = Evento.objects.create(
            titulo='Evento Passado',
            dt_evento=timezone.now() - timedelta(hours=1),
            usuario=self.user
        )
        self.assertTrue(evento_passado.get_evento_atrasado())

    def test_evento_proximo(self):
        """Testa se evento próximo é detectado corretamente"""
        # Evento em 30 minutos
        evento_proximo = Evento.objects.create(
            titulo='Evento Próximo',
            dt_evento=timezone.now() + timedelta(minutes=30),
            usuario=self.user
        )
        self.assertTrue(evento_proximo.get_evento_30min())
        
        # Evento em 2 horas
        self.assertFalse(self.evento.get_evento_30min())


class EventoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.evento = Evento.objects.create(
            titulo='Evento Teste',
            dt_evento=timezone.now() + timedelta(hours=2),
            usuario=self.user
        )

    def test_login_required(self):
        """Testa se o login é obrigatório para acessar as views"""
        response = self.client.get(reverse('agenda:lista'))
        self.assertEqual(response.status_code, 302)  # Redirect para login

    def test_lista_eventos_authenticated(self):
        """Testa se usuário logado consegue acessar lista de eventos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('agenda:lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evento Teste')

    def test_api_security(self):
        """Testa se a API está protegida contra acesso não autorizado"""
        # Tenta acessar sem login
        response = self.client.get(reverse('agenda:api_eventos', args=[self.user.id]))
        self.assertEqual(response.status_code, 401)  # Não autorizado
        
        # Cria outro usuário e tenta acessar dados do primeiro
        outro_user = User.objects.create_user(
            username='outro',
            password='testpass123'
        )
        self.client.login(username='outro', password='testpass123')
        response = self.client.get(reverse('agenda:api_eventos', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)  # Acesso negado

    def test_evento_creation(self):
        """Testa criação de evento via POST"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'titulo': 'Novo Evento',
            'dt_evento': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'descricao': 'Descrição do novo evento',
            'local': 'Local do evento'
        }
        response = self.client.post(reverse('agenda:submit_evento'), data)
        self.assertEqual(response.status_code, 302)  # Redirect após criação
        
        # Verifica se o evento foi criado
        self.assertTrue(
            Evento.objects.filter(titulo='Novo Evento', usuario=self.user).exists()
        )

    def test_timezone_handling(self):
        """Testa se o timezone está sendo tratado corretamente"""
        self.client.login(username='testuser', password='testpass123')
        
        # Criar evento com horário específico (19:00 horário local)
        data = {
            'titulo': 'Evento Timezone',
            'dt_evento': '2024-12-25T19:00',  # 19:00 local
            'descricao': 'Teste timezone',
            'local': 'São Paulo'
        }
        
        response = self.client.post(reverse('agenda:submit_evento'), data)
        self.assertEqual(response.status_code, 302)
        
        # Buscar o evento criado
        evento = Evento.objects.get(titulo='Evento Timezone')
        
        # Verificar se a hora local está correta (19:00 em São Paulo)
        br_timezone = pytz.timezone('America/Sao_Paulo')
        dt_local = evento.dt_evento.astimezone(br_timezone)
        
        self.assertEqual(dt_local.hour, 19)
        self.assertEqual(dt_local.minute, 0)
        
        # Verificar se o método retorna a data correta para o formulário
        expected_input = '2024-12-25T19:00'
        self.assertEqual(evento.get_data_input_evento(), expected_input)
