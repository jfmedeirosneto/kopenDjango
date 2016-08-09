#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.http import HttpResponse

from kopenDjango.produto.models import destaques_random
from kopenDjango.base.utils import SendContactFormThread, set_session_webview, delete_session_webview

def index(request):
    d = {}
    d.update(csrf(request))
    
    #Verifica busca
    d['busca'] = request.GET.get('busca', '').replace('+', '\s').title()
    
    #Verifica agent
    agent = request.GET.get('agent', '').lower()
    if agent == 'webview':
        set_session_webview(request)
    else:
        delete_session_webview(request)
    
    #Monta destaques    
    ofertasList = destaques_random()
    d['destaque1'] = None
    d['destaque2'] = None
    d['destaque3'] = None
    d['destaque4'] = None
    d['destaque5'] = None
    d['destaque6'] = None
    d['destaque7'] = None
    d['destaque8'] = None    
    d['destaque9'] = None
    d['destaque10'] = None    
    try:
        d['destaque1'] = ofertasList[0]
        d['destaque2'] = ofertasList[1]
        d['destaque3'] = ofertasList[2]
        d['destaque4'] = ofertasList[3]
        d['destaque5'] = ofertasList[4]
        d['destaque6'] = ofertasList[5]
        d['destaque7'] = ofertasList[6]
        d['destaque8'] = ofertasList[7]
        d['destaque9'] = ofertasList[8]
        d['destaque10'] = ofertasList[9]
    except IndexError:
        pass
        
    context = RequestContext(request)        
    return render_to_response('index.html',
                              d,
                              context_instance=context)
    
def noscript(request):
    d = {}
    d.update(csrf(request))
    context = RequestContext(request)        
    return render_to_response('noscript.html',
                              d,
                              context_instance=context)    

def dialog_contact_form(request):
    d = {}
    d.update(csrf(request))
    context = RequestContext(request)        
    return render_to_response('dialog_contact_form.html',
                              d,
                              context_instance=context)
    
def contact_form(request):
    d = {}

    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        mensagem = request.POST['mensagem']
        
        #Envia email para recuperar senha
        t = SendContactFormThread(request, nome, email, mensagem)
        t.start()        
        
        d['status'] = True
        d['message'] = 'Mensagem enviada com sucesso'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')                
