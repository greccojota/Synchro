# 📅 Nova Agenda - Sistema de Gerenciamento de Eventos

Uma aplicação web moderna para gerenciamento pessoal de eventos e compromissos, desenvolvida com Django e design responsivo.

## ✨ Funcionalidades

### 🎯 **Gerenciamento de Eventos**
- Criar, editar e excluir eventos
- Visualização de eventos futuros e histórico
- Campos personalizáveis: título, data/hora, descrição e local
- Status automático de eventos (normal, próximo, atrasado)

### 🗺️ **Busca Inteligente de Endereços**
- **Busca por CEP**: Integração com API ViaCEP
- **Geolocalização**: Detecção automática de localização atual
- **Preenchimento automático** de endereços completos
- Validação e formatação automática de CEP

### 🎨 **Design Moderno**
- Interface responsiva para desktop e mobile
- Sistema de design consistente com variáveis CSS
- Ícones intuitivos (Feather Icons)
- Gradientes e animações suaves

### 🔐 **Autenticação**
- Sistema de login seguro
- Proteção de rotas com decoradores
- Gestão de sessões
- Mensagens de feedback ao usuário

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.5
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Banco de Dados**: SQLite (desenvolvimento)
- **APIs Externas**: 
  - ViaCEP (busca por CEP)
  - Nominatim OpenStreetMap (geolocalização)
- **Ícones**: Feather Icons
- **Fonts**: Inter (Google Fonts)

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- pip

### 1. Navegue até o diretório do projeto
```bash
cd new-agenda/new_agenda
```

### 2. Crie e ative o ambiente virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute as migrações
```bash
python manage.py migrate
```

### 5. Crie um superusuário (opcional)
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor
```bash
python manage.py runserver
```

### 7. Acesse a aplicação
Abra seu navegador e vá para: `http://localhost:8000`

## 🎮 Como Usar

### **Login**
1. Acesse a página inicial
2. Faça login com suas credenciais
3. Você será redirecionado para a agenda principal

### **Gerenciar Eventos**
1. **Criar**: Clique em "Novo Evento" na página principal
2. **Editar**: Clique no botão "Editar" ao lado do evento
3. **Excluir**: Clique no botão "Excluir" ao lado do evento
4. **Histórico**: Acesse eventos passados em "Histórico"

### **Buscar Endereços**
1. No formulário de evento, no campo "Local":
2. **Por CEP**: Digite o CEP e clique em "Buscar CEP"
3. **Por Localização**: Clique em "Usar Localização" e permita o acesso
4. O endereço será preenchido automaticamente

## 📁 Estrutura do Projeto

```
new_agenda/
├── agenda/                     # App principal
│   ├── migrations/            # Migrações do banco
│   ├── __init__.py
│   ├── admin.py              # Configuração do admin
│   ├── apps.py               # Configuração do app
│   ├── models.py             # Modelos de dados
│   ├── tests.py              # Testes unitários
│   ├── urls.py               # URLs do app
│   └── views.py              # Views/Controllers
├── new_agenda/                # Configurações do projeto
│   ├── __init__.py
│   ├── asgi.py               # Configuração ASGI
│   ├── settings.py           # Configurações Django
│   ├── urls.py               # URLs principais
│   └── wsgi.py               # Configuração WSGI
├── static/                    # Arquivos estáticos
│   ├── css/
│   │   └── main.css          # Estilos principais
│   ├── js/
│   │   └── address-search.js # Funcionalidades de endereço
│   └── images/               # Imagens do projeto
├── templates/                 # Templates HTML
│   ├── agenda.html           # Página principal
│   ├── evento.html           # Formulário de evento
│   ├── historico.html        # Histórico de eventos
│   ├── login.html            # Página de login
│   └── model-page.html       # Template base
├── venv/                      # Ambiente virtual
├── db.sqlite3                 # Banco de dados SQLite
├── manage.py                  # Utilitário Django
├── requirements.txt           # Dependências
└── README.md                  # Este arquivo
```

## 🔧 Funcionalidades Técnicas

### **Models**
- **Evento**: Modelo principal com campos título, descrição, data/hora, local e usuário
- Métodos personalizados para formatação de data e verificação de status

### **Views**
- Views baseadas em funções com decoradores de autenticação
- Tratamento adequado de erros com `get_object_or_404`
- Sistema de mensagens para feedback ao usuário

### **URLs**
- Organização modular com namespaces
- URLs RESTful e semânticas
- Separação entre URLs do projeto e do app

### **Templates**
- Sistema de herança com template base
- Componentes reutilizáveis
- Design responsivo com CSS Grid e Flexbox

### **Static Files**
- CSS modular com variáveis personalizadas
- JavaScript organizado em módulos
- Otimização para produção

## 🔒 Segurança

- **Autenticação obrigatória** para todas as funcionalidades
- **Proteção CSRF** em todos os formulários
- **Validação de permissões** (usuários só acessam seus próprios dados)
- **Sanitização de dados** em formulários
- **Configurações seguras** para produção

## 🚀 Deploy

### Para Produção:
1. Configure `DEBUG = False` em settings.py
2. Configure `ALLOWED_HOSTS` com seu domínio
3. Use banco PostgreSQL ou MySQL
4. Configure servidor web (Nginx + Gunicorn)
5. Execute `python manage.py collectstatic`

### Variáveis de Ambiente Recomendadas:
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
DATABASE_URL = os.environ.get('DATABASE_URL')
```

## 📊 APIs Integradas

### **ViaCEP**
- Endpoint: `https://viacep.com.br/ws/{cep}/json/`
- Funcionalidade: Busca de endereço por CEP
- Gratuita e sem limitações

### **Nominatim OpenStreetMap**
- Endpoint: `https://nominatim.openstreetmap.org/reverse`
- Funcionalidade: Geolocalização reversa
- Gratuita com rate limiting

## 🧪 Testes

Para executar os testes:
```bash
python manage.py test
```

## 📈 Melhorias Futuras

- [ ] Sistema de notificações
- [ ] Integração com calendários externos
- [ ] API REST completa
- [ ] Aplicativo mobile
- [ ] Compartilhamento de eventos
- [ ] Sincronização em tempo real

## 👨‍💻 Autor

**João Victor Grecco**

## 📄 Licença

Este projeto é de uso livre para fins educacionais e pessoais.

---

⭐ **Projeto organizado e moderno para gerenciamento de eventos!**