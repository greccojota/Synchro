from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, CategoriaEvento, Evento, EventoRecorrente, NotificacaoEvento


class RegistroUsuarioForm(UserCreationForm):
    """Formulário customizado para registro de usuário"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Seu sobrenome'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Nome de usuário'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirme a senha'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Criar perfil do usuário
            PerfilUsuario.objects.create(usuario=user)
        return user


class PerfilUsuarioForm(forms.ModelForm):
    """Formulário para editar perfil do usuário"""
    class Meta:
        model = PerfilUsuario
        fields = ['telefone', 'foto', 'data_nascimento']
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '(11) 99999-9999'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            })
        }


class CategoriaEventoForm(forms.ModelForm):
    """Formulário para criar/editar categorias"""
    class Meta:
        model = CategoriaEvento
        fields = ['nome', 'cor', 'icone', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome da categoria'
            }),
            'cor': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'value': '#6366f1'
            }),
            'icone': forms.Select(attrs={
                'class': 'form-input'
            }, choices=[
                ('calendar', 'Calendário'),
                ('briefcase', 'Trabalho'),
                ('heart', 'Pessoal'),
                ('book', 'Estudos'),
                ('users', 'Reunião'),
                ('home', 'Casa'),
                ('car', 'Viagem'),
                ('coffee', 'Lazer'),
                ('activity', 'Exercício'),
                ('shopping-cart', 'Compras'),
            ]),
            'descricao': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Descrição da categoria (opcional)'
            })
        }


class EventoForm(forms.ModelForm):
    """Formulário melhorado para eventos"""
    class Meta:
        model = Evento
        fields = [
            'titulo', 'categoria', 'dt_evento', 'local', 'descricao', 
            'prioridade', 'evento_dia_todo', 'privado', 'cor_personalizada'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título do evento'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-input'
            }),
            'dt_evento': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Local do evento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Descrição do evento'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-input'
            }),
            'cor_personalizada': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color'
            }),
            'evento_dia_todo': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'privado': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar categorias apenas do usuário logado
            self.fields['categoria'].queryset = CategoriaEvento.objects.filter(
                usuario=user, ativo=True
            )


class EventoRecorrenteForm(forms.ModelForm):
    """Formulário para configurar eventos recorrentes"""
    class Meta:
        model = EventoRecorrente
        fields = ['tipo', 'intervalo', 'dias_semana', 'dia_mes', 'data_fim', 'max_ocorrencias']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-input'
            }),
            'intervalo': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'value': 1
            }),
            'dia_mes': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 31
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'max_ocorrencias': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1
            })
        }


class NotificacaoEventoForm(forms.ModelForm):
    """Formulário para configurar notificações"""
    class Meta:
        model = NotificacaoEvento
        fields = ['tipo', 'tempo_antecedencia', 'mensagem_customizada']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-input'
            }),
            'tempo_antecedencia': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'placeholder': 'Minutos antes'
            }),
            'mensagem_customizada': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Mensagem personalizada (opcional)'
            })
        }