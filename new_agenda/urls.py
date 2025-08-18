"""new_agenda URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from agenda import views as agenda_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Agenda URLs
    path('agenda/', include('agenda.urls')),
    
    # Authentication
    path('login/', agenda_views.login_user, name='login'),
    path('login/submit/', agenda_views.submit_login, name='submit_login'),
    path('registro/', agenda_views.registro_user, name='registro'),
    path('logout/', agenda_views.logout_user, name='logout'),
    
    # Redirect root to agenda
    path('', RedirectView.as_view(url='/agenda/', permanent=False), name='home'),
]

# Servir arquivos estáticos e media durante desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
