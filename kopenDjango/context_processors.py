#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.conf import settings

from kopenDjango.cidade.models import Cidade
from kopenDjango.usuario.utils import get_session_user
from kopenDjango.base.utils import get_session_webview
from kopenDjango.settings import FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

def main(request):
    d = {}
    
    #Usuario
    d['kopen_user'] = get_session_user(request)
            
    #Cidades
    d['cidades'] = Cidade.objects.filter(active=True).order_by('id')
        
    #Dados do Site
    d['protocol'] = "http://" if request.is_secure else "https://"
    d['media_root'] = settings.MEDIA_ROOT
    d['media_dir'] = settings.MEDIA_DIR
    d['domain'] = request.get_host()
    d['site_name'] = "kopenDjango"
    if Site.objects.count() > 0:
        main_site = Site.objects.get(id=1);
        if main_site:
            d['site_name'] = main_site.name
    d['admin_name'] = "kopenDjango"
    d['admin_email'] = "kopen@kopen.mobi"
    if User.objects.count() > 0:
        admin_user = User.objects.get(id=1);
        if admin_user:
            d['admin_name'] = admin_user.get_full_name()            
            d['admin_email'] = admin_user.email
            
    #Dados do Facebook
    d['facebook_client_id'] = FACEBOOK_CLIENT_ID
    d['facebook_client_secret'] = FACEBOOK_CLIENT_SECRET
      
    #WebView
    d['webview'] = get_session_webview(request)    
    
    return d        
