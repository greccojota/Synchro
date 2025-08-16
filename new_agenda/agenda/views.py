from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta

from .models import Evento

def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('agenda:lista')
        else:
            messages.error(request, 'Usuário ou Senha Inválido.')

    return redirect('login')

@login_required(login_url='/login/')
def lista_eventos(request):
    """Lista eventos futuros do usuário logado"""
    dt_atual = datetime.now() - timedelta(days=1)
    eventos = Evento.objects.filter(
        usuario=request.user,
        dt_evento__gt=dt_atual
    ).order_by('dt_evento')
    
    context = {'eventos': eventos}
    return render(request, 'agenda.html', context)

@login_required(login_url='/login/')
def historico_eventos(request):
    """Lista eventos passados do usuário logado"""
    dt_atual = datetime.now() - timedelta(days=1)
    eventos = Evento.objects.filter(
        usuario=request.user,
        dt_evento__lt=dt_atual
    ).order_by('-dt_evento')
    
    context = {'eventos': eventos}
    return render(request, 'historico.html', context)

@login_required(login_url='/login/')
def evento(request):
    """Exibe formulário para criar ou editar evento"""
    id_evento = request.GET.get('id')
    context = {}
    
    if id_evento:
        evento = get_object_or_404(Evento, id=id_evento, usuario=request.user)
        context['evento'] = evento
    
    return render(request, 'evento.html', context)

@login_required(login_url='/login/')
def submit_evento(request):
    """Processa criação ou edição de evento"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        dt_evento = request.POST.get('dt_evento')
        descricao = request.POST.get('descricao')
        local = request.POST.get('local')
        id_evento = request.POST.get('id_evento')

        try:
            if id_evento:
                # Atualizar evento existente
                evento = get_object_or_404(Evento, id=id_evento, usuario=request.user)
                evento.titulo = titulo
                evento.dt_evento = dt_evento
                evento.descricao = descricao
                evento.local = local
                evento.save()
                messages.success(request, 'Evento atualizado com sucesso!')
            else:
                # Criar novo evento
                Evento.objects.create(
                    titulo=titulo,
                    dt_evento=dt_evento,
                    descricao=descricao,
                    local=local,
                    usuario=request.user
                )
                messages.success(request, 'Evento criado com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao salvar evento. Tente novamente.')

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