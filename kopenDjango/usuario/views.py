#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import urllib2
import urlparse

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import simplejson
from django.template import RequestContext
from django.shortcuts import render_to_response

from kopenDjango.usuario.models import Usuario
from kopenDjango.base.utils import SendRequestPasswordThread, get_random_string
from kopenDjango.usuario.utils import set_session_user, delete_session_user, get_session_user, set_facebook_acess_token, delete_facebook_acess_token
from kopenDjango.settings import FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

def dialog_change_user(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_change_user.html',
                              d,
                              context_instance=context)
    
def dialog_user_points(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_user_points.html',
                              d,
                              context_instance=context)    
    
def dialog_top_users(request):
    d = {}
    
    top_users = Usuario.objects.filter(active=True).order_by("-points")[0:9]
    d['top_users'] = top_users
    
    context = RequestContext(request)        
    return render_to_response('dialog_top_users.html',
                              d,
                              context_instance=context)
    
def dialog_login(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_login.html',
                              d,
                              context_instance=context)    
    
def dialog_request_password(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_request_password.html',
                              d,
                              context_instance=context)    

def dialog_register_user(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_register_user.html',
                              d,
                              context_instance=context)
      
def dialog_termos_uso(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_termos_uso.html',
                              d,
                              context_instance=context)

def login(request):
    d = {}

    delete_session_user(request)
    delete_facebook_acess_token(request)
        
    if request.method == 'POST':
        user = request.POST['user']
        password = request.POST['password']
        
        if user and password:
            #Verifica se usuario existe
            try:
                userObject = Usuario.objects.get(user=user)
                
                if not userObject.active:
                    d['status'] = False
                    d['message'] = 'Usuário bloqueado'
                    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                
                if password == userObject.password:
                    userObject.failures = 0
                    userObject.save()
                    
                    d['status'] = True
                    d['message'] = 'Entrou com sucesso'
                    set_session_user(request, userObject)
                    return HttpResponse(simplejson.dumps(d), mimetype='text/html')                
                else:
                    userObject.failures = userObject.failures + 1
                    d['status'] = False                
                    if userObject.failures > 3:
                        userObject.active = False
                        d['message'] = 'Senha incorreta, Usuário bloqueado'
                    elif userObject.failures > 2:
                        d['message'] = 'Senha incorreta, Última tentativa antes de bloquear usuário'                        
                    else:
                        d['message'] = 'Senha incorreta'
                    userObject.save()
                    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    
            except ObjectDoesNotExist:
                d['status'] = False
                d['message'] = 'Usuário não existe'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        else:
            d['status'] = False
            d['message'] = 'Formulário incompleto'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
    
def request_password(request):
    d = {}
    
    delete_session_user(request)
    delete_facebook_acess_token(request)
    
    if request.method == 'POST':    
        email = request.POST['email']
        
        if email:
            #Verifica email
            try:
                userObject = Usuario.objects.get(email=email)
                
                #Envia email para recuperar senha
                t = SendRequestPasswordThread(request, userObject)
                t.start()
                
                d['status'] = True
                d['message'] = 'Link para recuperar senha enviado com sucesso para seu email'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            except ObjectDoesNotExist:
                d['status'] = False
                d['message'] = 'E-mail não cadastrado'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        else:
            d['status'] = False
            d['message'] = 'Formulário incompleto'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')    
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    
def logout(request):
    d = {}
    
    delete_session_user(request)
    delete_facebook_acess_token(request)
    
    d['status'] = True
    d['message'] = 'Você saiu com sucesso'
    
    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
def register(request):
    d = {}
    
    delete_session_user(request)
    delete_facebook_acess_token(request)
    
    if request.method == 'POST':    
        user = request.POST['user']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        chklicense = request.POST.get('chklicense', None)
        
        if user and name and email and password and chklicense:
            #Verifica se usuario ja existe
            try:
                Usuario.objects.get(user=user)
                d['status'] = False
                d['message'] = 'Nome de usuário já registrado'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            except ObjectDoesNotExist:
                pass
            
            #Verifica se email ja existe
            try:
                Usuario.objects.get(email=email)
                d['status'] = False
                d['message'] = 'E-mail já utilizado por outro usuário'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            except ObjectDoesNotExist:
                pass
            
            #Verifica tamanho da senha
            if len(password) < 6:
                d['status'] = False
                d['message'] = 'Mínimo 6 caracteres para senha'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            
            #Cria novo usuario
            userObject = Usuario.objects.create(user=user,
                                       name=name,
                                       email=email,
                                       password=password)
            userObject.save()
            
            d['status'] = True
            d['message'] = 'Novo usuário registrado com sucesso'
            set_session_user(request, userObject)
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        else:
            d['status'] = False
            d['message'] = 'Formulário incompleto'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
def change_user(request):
    d = {}
    
    if request.method == 'POST':    
        user_id = request.POST['id']
        user = request.POST['user']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        
        if user_id and user and name and email:
            #Verifica se esta logado
            session_user = get_session_user(request)
            if session_user == None:
                d['status'] = False
                d['message'] = 'Usuário não está conectado'
                delete_session_user(request)
                delete_facebook_acess_token(request)
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            
            #Verifica usuario atual
            try:
                change_user = Usuario.objects.get(id__exact=user_id)
            except ObjectDoesNotExist:
                d['status'] = False
                d['message'] = 'Não existe usuário para esse registro'
                delete_session_user(request)
                delete_facebook_acess_token(request)
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
            #Verifica se esta tentando alterar outro usuario
            if change_user != session_user:
                d['status'] = False
                d['message'] = 'Acesso ao dados do usuário negado'
                delete_session_user(request)
                delete_facebook_acess_token(request)
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            
            #Caso mudou nome de usuario verifica se novo usuario ja existe
            if change_user.user != user:
                try:
                    Usuario.objects.get(user=user)
                    d['status'] = False
                    d['message'] = 'Nome de usuário já registrado'
                    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                except ObjectDoesNotExist:
                    pass
            
            #Caso mudou email verifica se novo email ja existe
            if change_user.email != email:
                try:
                    Usuario.objects.get(email=email)
                    d['status'] = False
                    d['message'] = 'E-mail já utilizado por outro usuário'
                    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                except ObjectDoesNotExist:
                    pass
                
            #Verifica tamanho da senha
            if (len(password) != 0) and (len(password) < 6):
                d['status'] = False
                d['message'] = 'Mínimo 6 caracteres para senha'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            
            #Atualiza dados do usuario
            change_user.user = user
            change_user.name = name
            change_user.email = email
            if len(password) != 0:
                change_user.password = password
            change_user.save()
            
            d['status'] = True
            d['message'] = 'Dados do usuário alterados com sucesso'
            set_session_user(request, change_user)
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        else:
            d['status'] = False
            d['message'] = 'Formulário incompleto'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')    
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    
def dialog_change_password(request, user_id, password_hash):
    d = {}
    
    delete_session_user(request)
    delete_facebook_acess_token(request)

    if user_id and password_hash:
        #Verifica se usuario existe
        try:
            change_user = Usuario.objects.get(id__exact=user_id)
            
            #Verifica password_hash
            if change_user.password_hash != password_hash:
                change_user = None

        except ObjectDoesNotExist:
            change_user = None
    else:
        change_user = None

    d['change_user'] = change_user
    context = RequestContext(request)
    return render_to_response('dialog_change_password.html',
                              d,
                              context_instance=context)
    
def change_password(request):
    d = {}
    
    delete_session_user(request)
    delete_facebook_acess_token(request)
        
    if request.method == 'POST':    
        user_id = request.POST['id']
        user = request.POST['user']
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        
        if user_id and user and name and email and password:
            #Verifica usuario atual
            try:
                change_user = Usuario.objects.get(id__exact=user_id)
            except ObjectDoesNotExist:
                d['status'] = False
                d['message'] = 'Não existe usuário para esse registro'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                
            #Verifica tamanho da senha
            if len(password) < 6:
                d['status'] = False
                d['message'] = 'Mínimo 6 caracteres para senha'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            
            #Atualiza senha do usuario e ajusta seu estado
            change_user.password = password
            change_user.failures = 0
            change_user.active = True
            change_user.password_hash = None
            change_user.save()
            
            d['status'] = True
            d['message'] = 'Senha alterada com sucesso'
            set_session_user(request, change_user)
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        else:
            d['status'] = False
            d['message'] = 'Formulário incompleto'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')    
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')

#Via Facebook Graph Oauth API 
def facebook_authorize(request):
    d = {}
    
    delete_facebook_acess_token(request)
        
    protocol = "http://" if request.is_secure else "https://"
    domain = request.get_host()
    d['redirect'] = protocol + domain
    
    context = RequestContext(request)
        
    #Codigo acesso Facebook (Aplicativo Conectado pelo Usuario)
    if request.GET.has_key('code'):
        facebook_code = request.GET['code']
    else:
        facebook_code = None
    
    #Parametro passado no link inicial "graph.facebook.com/oauth/authorize"
    if request.GET.has_key('state'):
        facebook_state = request.GET['state']
    else:
        facebook_state = None
        
    if facebook_code and facebook_state:
        #URL para solicitar o Access Token
        acess_url = '%s?redirect_uri=%s%s%s&client_id=%s&code=%s&client_secret=%s' %\
                    ('https://graph.facebook.com/oauth/access_token',
                     protocol,
                     domain,
                     '/facebook_authorize/',
                     FACEBOOK_CLIENT_ID,
                     facebook_code,
                     FACEBOOK_CLIENT_SECRET)
        facebook_access_token = None
        
        #Leitura do Access Token (Acesso Autorizado)
        try:
            urlopen = urllib2.urlopen(acess_url, timeout=5)
            read_access_token = urlopen.read()
            if read_access_token.startswith('access_token'):
                parameters = urlparse.parse_qs(read_access_token)
                if parameters.has_key('access_token'):
                    facebook_access_token = parameters['access_token'][0]
                    set_facebook_acess_token(request, facebook_access_token)
        except:
            d['message'] = 'Falha leitura códido de acesso'
            return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)            
            
        if facebook_access_token:
            #URL para solicitar dados do usuario conectado
            me_url = '%s?access_token=%s' %\
                    ('https://graph.facebook.com/me',
                     facebook_access_token)
            facebook_id = None
            
            #Leitura dados do usuario conectado
            try:
                urlopen = urllib2.urlopen(me_url, timeout=5)
                read_me = urlopen.read()
                user_data = simplejson.loads(read_me)
                if user_data.has_key('id'):
                    facebook_id = user_data['id']
                    facebook_user = user_data['username']
                    facebook_name = user_data['name']
                    facebook_email = user_data['email']
            except:
                d['message'] = 'Falha leitura dados do usúario'
                return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)                 
                
            if facebook_id and facebook_user and facebook_name and facebook_email:
                if facebook_state == 'login':
                    delete_session_user(request)
                        
                    #Verifica usuario para login
                    try:
                        userObject = Usuario.objects.get(facebook_id__exact=facebook_id)
                        userObject.failures = 0
                        userObject.save()
                        set_session_user(request, userObject)
                        d['message'] = 'Entrou com sucesso'
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)            
                    except ObjectDoesNotExist:
                        d['message'] = 'Não existe usuário registrado para essa conta do Facebook, Registre-se no site primeiro'
                        d['redirect'] = protocol + domain + "/dialog_register_user/"
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                    
                elif facebook_state == 'register':
                    delete_session_user(request)
                    
                    #Verifica se id do Facebook ja existe
                    try:
                        Usuario.objects.get(facebook_id__exact=facebook_id)
                        d['message'] = 'Conta do Facebook já registrada, Você pode entrar no site'
                        d['redirect'] = protocol + domain + "/dialog_login/"
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                    except ObjectDoesNotExist:
                        pass
                    
                    #Verifica se usuario ja existe
                    try:
                        Usuario.objects.get(user=facebook_user)
                        #Tenta versao alternativa do usuario
                        facebook_user = facebook_user + "_" + get_random_string(4)
                        Usuario.objects.get(user=facebook_user)
                        d['message'] = 'Nome de usuário já registrado'
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                    except ObjectDoesNotExist:
                        pass
                    
                    #Verifica se email ja existe
                    try:
                        Usuario.objects.get(email=facebook_email)
                        d['message'] = 'E-mail já utilizado por outro usuário'
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                    except ObjectDoesNotExist:
                        pass
                    
                    #Cria senha aleatoria para usuario
                    password = get_random_string(8)
                    
                    #Cria novo usuario
                    userObject = Usuario.objects.create(facebook_id=facebook_id,
                                                        user=facebook_user,
                                                        name=facebook_name,
                                                        email=facebook_email,
                                                        password=password)
                    userObject.save()
                    d['message'] = 'Novo usuário registrado com sucesso'
                    set_session_user(request, userObject)
                    return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                
                elif facebook_state == 'connect':
                    #Verifica se esta logado
                    session_user = get_session_user(request)
                    if session_user == None:
                        d['message'] = 'Usuário não está conectado, Entrar primeiro'
                        d['redirect'] = protocol + domain + "/dialog_login/"
                        return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                            
                    #Verifica se id do Facebook ja existe
                    try:
                        userObject = Usuario.objects.get(facebook_id__exact=facebook_id)
                        #Verifica se eh o mesmo usuario conectado
                        if userObject == session_user:
                            d['message'] = 'Conectado ao Facebook com sucesso'
                            return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)                    
                        else:
                            d['message'] = 'Conta do Facebook já registrada, Selecione outra conta do Facebook'
                            return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                    except ObjectDoesNotExist:
                        pass
                    
                    #Armazena dados do facebook no usuario logado
                    session_user.facebook_id = facebook_id
                    session_user.save()
                    d['message'] = 'Conectado ao Facebook com sucesso'
                    return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)        
                            
            else:
                d['message'] = 'Dados usúario inválidos'
                return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)
                            
    d['message'] = 'Acesso não autorizado'
    return render_to_response('dialog_facebook_authorize.html', d, context_instance=context)