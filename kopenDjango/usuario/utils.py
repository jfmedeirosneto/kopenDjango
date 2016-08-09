#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.core.exceptions import ObjectDoesNotExist

from kopenDjango.usuario.models import Usuario

KOPEN_USER_ID = 'kopenDjango-UserId-Session-1ePaIY4s'
KOPEN_FACEBOOK_ACCESS_TOKEN = 'kopenDjango-Facebook-AccessToken-1ePaIY4s'

# Funcao para setar o userid no session cookie
def set_session_user(request, user):
    request.session[KOPEN_USER_ID] = user.id

# Funcao para remover o userid do session cookie
def delete_session_user(request):
    try:
        del request.session[KOPEN_USER_ID]
    except KeyError:
        pass
        
# Funcao para retornar o user do session cookie
def get_session_user(request):
    if request.session.get(KOPEN_USER_ID):
        try:
            kopen_user_id = request.session[KOPEN_USER_ID]
            user = Usuario.objects.get(id__exact=kopen_user_id)
            return user
        except ObjectDoesNotExist:
            return None
    else:
        return None
    
# Funcao para setar o facebook access token no session cookie
def set_facebook_acess_token(request, facebook_access_token):
    request.session[KOPEN_FACEBOOK_ACCESS_TOKEN] = facebook_access_token

# Funcao para remover o facebook access token do session cookie
def delete_facebook_acess_token(request):
    try:
        del request.session[KOPEN_FACEBOOK_ACCESS_TOKEN]
    except KeyError:
        pass
    
# Funcao para retornar o facebook access token do session cookie
def get_session_facebook_access_token(request):
    if request.session.get(KOPEN_FACEBOOK_ACCESS_TOKEN):
        return request.session[KOPEN_FACEBOOK_ACCESS_TOKEN]
    else:
        return None