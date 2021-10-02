from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect
from agenda.models import Evento
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, timedelta
from django.http.response import Http404, JsonResponse
# Create your views here.

def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('/')

def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, 'Usuário ou Senha Inválido.')

    return redirect('/') #redireciona para a pagina principal

@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user

    #try:
    dt_atual = datetime.now() - timedelta(days=1)  # datas que venceram no dia
    dt_atual = dt_atual.strftime('%Y-%m-%d %H:%M:%S') 
    evento = Evento.objects.filter(usuario=usuario,dt_evento__gt=dt_atual)  # consultando dados no BD - __gt para maior e __lt para menor (comparação);
    dados = {'eventos': evento}
    return render(request, 'agenda.html', dados)

    # except Exception:
    #     raise Http404

@login_required(login_url='/login/')
def historico_eventos(request):
    usuario = request.user

    try:
        dt_atual = datetime.now() - timedelta(days=1)  # datas que venceram no dia
        evento = Evento.objects.filter(usuario=usuario,dt_evento__lt=dt_atual)  # consultando dados no BD - __gt para maior e __lt para menor (comparação);
        dados = {'eventos': evento}
        print(evento)
        return render(request, 'historico.html', dados)

    except Exception:
        raise Http404

@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    dados = {}
    if id_evento:
        dados['evento'] = Evento.objects.get(id=id_evento)
    return render(request, 'evento.html', dados)

@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        titulo = request.POST.get('titulo')
        dt_evento = request.POST.get('dt_evento')
        descricao = request.POST.get('descricao')
        local = request.POST.get('local')
        usuario = request.user
        id_evento = request.POST.get('id_evento')

        try:

            if id_evento:
                Evento.objects.filter(id=id_evento).update(titulo=titulo, dt_evento=dt_evento, descricao=descricao, local=local)

                # ABAIXO ESTA UMA OUTRA OPCAO DE FAZER UMA ALTERAÇÃO/UPDATE;
                # evento = Evento.objects.get(id=id_evento)
                # if evento.usuario == usuario:
                #     evento.titulo = titulo
                #     evento.dt_evento = dt_evento
                #     evento.descricao = descricao
                #     evento.local = local
                #     evento.save()

            else:
                Evento.objects.create(titulo=titulo, dt_evento=dt_evento, descricao=descricao, local=local, usuario=usuario) #inserindo dados na tabela evendo no BD

        except Exception:
            raise Http404

    return redirect('/')

@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user

    try:
        evento = Evento.objects.get(id=id_evento)

        if usuario == evento.usuario:
            evento.delete()
        else:
            raise Http404()

    except Exception:
        raise Http404

    return redirect('/')

def json_lista_evento(request, id_usuario):
    usuario = User.objects.get(id=id_usuario)
    evento = Evento.objects.filter(usuario=usuario).values('id','titulo')
    return JsonResponse(list(evento), safe=False)

# def index(request):
#     return redirect('admin/')

#def do exercicio da aula 5 - Criando tabelas com models
# def localEvento(request, titulo_evento):
#     try:
#         evento = Evento.objects.get(titulo=titulo_evento)
#         return HttpResponse('<h3>Local da Consulta: {}<h3>'.format(evento.local))
#     except Exception:
#         import traceback
#         print(traceback.format_exc())
#         return HttpResponse('<h3>Titulo de Evento Inválido<h3>')
