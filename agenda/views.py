from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Evento, PerfilUsuario, CategoriaEvento, EventoRecorrente, NotificacaoEvento
)
from .forms import (
    RegistroUsuarioForm, PerfilUsuarioForm, CategoriaEventoForm, 
    EventoForm, EventoRecorrenteForm, NotificacaoEventoForm
)

def login_user(request):
    return render(request, 'login.html')


def registro_user(request):
    """View para registro de novos usuários"""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar categorias padrão para o usuário
            categorias_padrao = [
                {'nome': 'Trabalho', 'cor': '#3b82f6', 'icone': 'briefcase'},
                {'nome': 'Pessoal', 'cor': '#ef4444', 'icone': 'heart'},
                {'nome': 'Estudos', 'cor': '#10b981', 'icone': 'book'},
                {'nome': 'Reunião', 'cor': '#f59e0b', 'icone': 'users'},
            ]
            
            for cat_data in categorias_padrao:
                CategoriaEvento.objects.create(
                    usuario=user,
                    nome=cat_data['nome'],
                    cor=cat_data['cor'],
                    icone=cat_data['icone']
                )
            
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'auth/registro.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')

def submit_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            usuario = authenticate(username=username, password=password)
            
            if usuario is not None:
                login(request, usuario)
                return redirect('agenda:lista')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return redirect('login')

@login_required(login_url='/login/')
def lista_eventos(request):
    """Lista eventos futuros do usuário logado"""
    dt_atual = timezone.now() - timedelta(days=1)
    eventos = Evento.objects.filter(
        usuario=request.user,
        dt_evento__gt=dt_atual
    ).order_by('dt_evento')
    
    # Garantir que o perfil existe
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    context = {
        'eventos': eventos,
        'perfil': perfil
    }
    return render(request, 'agenda/lista.html', context)

@login_required(login_url='/login/')
def historico_eventos(request):
    """Lista eventos passados do usuário logado"""
    dt_atual = timezone.now() - timedelta(days=1)
    eventos = Evento.objects.filter(
        usuario=request.user,
        dt_evento__lt=dt_atual
    ).order_by('-dt_evento')
    
    context = {'eventos': eventos}
    return render(request, 'agenda/historico.html', context)

@login_required(login_url='/login/')
def evento(request):
    """Exibe formulário para criar ou editar evento"""
    id_evento = request.GET.get('id')
    evento_obj = None
    
    if id_evento:
        evento_obj = get_object_or_404(Evento, id=id_evento, usuario=request.user)
    
    # Verificar limite de eventos para usuários gratuitos
    perfil = getattr(request.user, 'perfil', None)
    if not perfil:
        # Criar perfil se não existir
        perfil = PerfilUsuario.objects.create(usuario=request.user)
    
    if not evento_obj and not perfil.pode_criar_evento():
        messages.error(request, f'Você atingiu o limite de {perfil.limite_eventos_mes} eventos por mês do plano gratuito. Considere fazer upgrade!')
        return redirect('agenda:lista')
    
    form = EventoForm(user=request.user, instance=evento_obj)
    recorrencia_form = EventoRecorrenteForm()
    
    context = {
        'evento': evento_obj,
        'form': form,
        'recorrencia_form': recorrencia_form,
        'categorias': CategoriaEvento.objects.filter(usuario=request.user, ativo=True),
        'perfil': perfil
    }
    
    return render(request, 'agenda/evento.html', context)

@login_required(login_url='/login/')
def submit_evento(request):
    """Processa criação ou edição de evento"""
    if request.method == 'POST':
        id_evento = request.POST.get('id_evento')
        evento_obj = None
        
        if id_evento:
            evento_obj = get_object_or_404(Evento, id=id_evento, usuario=request.user)
        
        form = EventoForm(user=request.user, data=request.POST, instance=evento_obj)
        
        if form.is_valid():
            evento = form.save(commit=False)
            evento.usuario = request.user
            evento.save()
            
            # Processar recorrência se especificada
            criar_recorrencia = request.POST.get('criar_recorrencia')
            if criar_recorrencia and not evento_obj:  # Só para novos eventos
                recorrencia_form = EventoRecorrenteForm(request.POST)
                if recorrencia_form.is_valid():
                    recorrencia = recorrencia_form.save(commit=False)
                    recorrencia.evento_base = evento
                    recorrencia.save()
                    
                    # Gerar eventos futuros baseados na recorrência
                    ocorrencias = recorrencia.gerar_proximas_ocorrencias(limite=20)
                    eventos_criados = 0
                    
                    for data_ocorrencia in ocorrencias[:10]:  # Limitar a 10 eventos futuros
                        Evento.objects.create(
                            titulo=evento.titulo,
                            descricao=evento.descricao,
                            dt_evento=data_ocorrencia,
                            local=evento.local,
                            categoria=evento.categoria,
                            prioridade=evento.prioridade,
                            evento_dia_todo=evento.evento_dia_todo,
                            privado=evento.privado,
                            cor_personalizada=evento.cor_personalizada,
                            usuario=request.user
                        )
                        eventos_criados += 1
                    
                    messages.success(request, f'Evento recorrente criado! {eventos_criados + 1} eventos foram gerados.')
                else:
                    messages.warning(request, 'Evento criado, mas houve erro na configuração de recorrência.')
            else:
                action = 'atualizado' if evento_obj else 'criado'
                messages.success(request, f'Evento {action} com sucesso!')
        else:
            messages.error(request, 'Erro ao salvar evento. Verifique os dados informados.')
            return render(request, 'agenda/evento.html', {
                'form': form,
                'evento': evento_obj,
                'categorias': CategoriaEvento.objects.filter(usuario=request.user, ativo=True)
            })

    return redirect('agenda:lista')

@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    """Deleta evento do usuário"""
    evento = get_object_or_404(Evento, id=id_evento, usuario=request.user)
    evento.delete()
    messages.success(request, 'Evento excluído com sucesso!')
    return redirect('agenda:lista')

def json_lista_evento(request, id_usuario):
    """API endpoint para listar eventos de um usuário (JSON)"""
    usuario = get_object_or_404(User, id=id_usuario)
    eventos = Evento.objects.filter(usuario=usuario).values('id', 'titulo')
    return JsonResponse(list(eventos), safe=False)


@login_required(login_url='/login/')
def perfil_usuario(request):
    """View para editar perfil do usuário"""
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('agenda:perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'form': form,
        'perfil': perfil,
        'eventos_mes': perfil.eventos_criados_mes(),
    }
    return render(request, 'agenda/perfil.html', context)


@login_required(login_url='/login/')
def categorias_evento(request):
    """View para listar e gerenciar categorias"""
    categorias = CategoriaEvento.objects.filter(usuario=request.user, ativo=True)
    
    if request.method == 'POST':
        form = CategoriaEventoForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('agenda:categorias')
    else:
        form = CategoriaEventoForm()
    
    context = {
        'categorias': categorias,
        'form': form
    }
    return render(request, 'agenda/categorias.html', context)


@login_required(login_url='/login/')
def editar_categoria(request, categoria_id):
    """View para editar categoria específica"""
    categoria = get_object_or_404(CategoriaEvento, id=categoria_id, usuario=request.user)
    
    if request.method == 'POST':
        form = CategoriaEventoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('agenda:categorias')
    else:
        form = CategoriaEventoForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria
    }
    return render(request, 'agenda/editar_categoria.html', context)


@login_required(login_url='/login/')
def deletar_categoria(request, categoria_id):
    """View para deletar categoria"""
    categoria = get_object_or_404(CategoriaEvento, id=categoria_id, usuario=request.user)
    
    if request.method == 'POST':
        # Verificar se há eventos usando esta categoria
        eventos_com_categoria = Evento.objects.filter(categoria=categoria).count()
        if eventos_com_categoria > 0:
            messages.warning(request, f'Não é possível excluir a categoria "{categoria.nome}" pois ela está sendo usada em {eventos_com_categoria} evento(s).')
        else:
            categoria.delete()
            messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso!')
    
    return redirect('agenda:categorias')


@login_required(login_url='/login/')
def dashboard(request):
    """Dashboard com estatísticas do usuário"""
    perfil = getattr(request.user, 'perfil', None)
    if not perfil:
        perfil = PerfilUsuario.objects.create(usuario=request.user)
    
    # Estatísticas
    hoje = timezone.now().date()
    eventos_hoje = Evento.objects.filter(
        usuario=request.user, 
        dt_evento__date=hoje
    ).count()
    
    eventos_semana = Evento.objects.filter(
        usuario=request.user,
        dt_evento__date__gte=hoje,
        dt_evento__date__lt=hoje + timedelta(days=7)
    ).count()
    
    eventos_mes = perfil.eventos_criados_mes()
    
    eventos_atrasados = Evento.objects.filter(
        usuario=request.user,
        dt_evento__lt=timezone.now(),
        concluido=False
    ).count()
    
    # Eventos por categoria
    eventos_por_categoria = CategoriaEvento.objects.filter(
        usuario=request.user, ativo=True
    ).annotate(
        total_eventos=Count('eventos')
    ).order_by('-total_eventos')[:5]
    
    context = {
        'perfil': perfil,
        'eventos_hoje': eventos_hoje,
        'eventos_semana': eventos_semana,
        'eventos_mes': eventos_mes,
        'eventos_atrasados': eventos_atrasados,
        'eventos_por_categoria': eventos_por_categoria,
        'limite_mensal': perfil.limite_eventos_mes,
        'pode_criar_evento': perfil.pode_criar_evento()
    }
    
    return render(request, 'agenda/dashboard.html', context)