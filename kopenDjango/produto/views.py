#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from threading import Thread
from decimal import Decimal, InvalidOperation
from locale import atof
import re, datetime

from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.shortcuts import render_to_response

from kopenDjango.cidade.models import Cidade
from kopenDjango.produto.models import Produto, Local, Oferta, ErroOferta
from kopenDjango.usuario.models import Usuario
from kopenDjango.base.utils import timenow, SendAddOfertaThread, SendSuggestProdutoThread, SendErroOfertaThread
from kopenDjango.usuario.utils import get_session_user

#Thread para marcar ofertas procuradas
class OfertaSearchedThread(Thread):
    def __init__ (self,ofertasList):
        Thread.__init__(self)
        self.ofertasList = ofertasList
        
    def run(self):
        #Marca ofertas como buscada
        for ofertaObject in self.ofertasList:
            ofertaObject.searched = ofertaObject.searched + 1
            ofertaObject.save()
            
def ajax_produtos(request):
    l = []
    busca = request.GET['busca']
    cidade = request.GET['cidade']
    ativos = int(request.GET['ativos'])
    
    #Verifica cidade
    try:
        cidadeObject = Cidade.objects.get(active=True, id__exact=cidade)
    except ObjectDoesNotExist:
        return HttpResponse(simplejson.dumps(l), mimetype='text/html')
    
    def processProdutoQuery(produtoQuery):
        for produtoObject in produtoQuery:
            #Tratar somente ativos
            if ativos:
                #Tem oferta ativa para esse produto nessa cidade
                month_ago = timenow() - datetime.timedelta(days=30)
                ofertaQuery = produtoObject.ofertas.\
                    filter(cidade=cidadeObject, active=True, user__active=True, local__active=True).\
                    exclude(created__lt=month_ago)
                if ofertaQuery.count() > 0:
                    #Adiciona a lista
                    key = produtoObject.nome.title()
                    if key not in l:
                        l.append(key)
            else:
                #Adiciona a lista
                key = produtoObject.nome.title()
                if key not in l:
                    l.append(key)                
                
    
    #Filtra texto inteiro
    produtoQuery = Produto.objects.filter(active=True, nome__icontains=busca).order_by('nome')
    processProdutoQuery(produtoQuery)
            
    #Filtra fragmentos do texto
    fragments = re.findall(r"[\w']+", busca)
    for fragment in fragments:
        if (len(fragment) > 2) and (fragment != busca):
            produtoQuery = Produto.objects.filter(active=True, nome__icontains=fragment).order_by('nome')
            processProdutoQuery(produtoQuery)            
        
    response = HttpResponse(simplejson.dumps(l), mimetype='text/html')
    return response

def ajax_locais(request):
    l = []
    busca = request.GET['busca']
    
    #Filtra texto inteiro
    localQuery = Local.objects.filter(active=True, nome__icontains=busca).order_by('nome')
    for local in localQuery:
        key = local.nome.title()
        if key not in l:
            l.append(key)
            
    #Filtra fragmentos do texto
    fragments = re.findall(r"[\w']+", busca)
    for fragment in fragments:
        if len(fragment) > 2:
            localQuery = Local.objects.filter(active=True, nome__icontains=fragment).order_by('nome')
            for local in localQuery:
                key = local.nome.title()
                if key not in l:
                    l.append(key)            
        
    response = HttpResponse(simplejson.dumps(l), mimetype='text/html')
    return response

def ajax_check_local(request):
    d = {}
    
    local = request.GET['local']
    
    #Verifica tamanho do local
    if len(local) < 3:    
        d['status'] = False
        d['message'] = 'Local com nome muito curto'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
    #Verifica local
    try:
        Local.objects.get(active=True, nome__iexact=local.title())
        d['status'] = True
        d['message'] = 'Local já cadastrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
    except ObjectDoesNotExist:
        d['status'] = False
        d['message'] = 'Local não existe'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                
def ajax_check_produto(request):
    d = {}

    produto = request.GET['produto']
    
    #Verifica tamanho do nome do produto
    if len(produto) < 3:
        d['status'] = False
        d['message'] = 'Produto com nome muito curto'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
    #Verifica produto ativo
    try:
        Produto.objects.get(active=True, nome__iexact=produto.title())
        d['status'] = True
        d['message'] = 'Produto já cadastrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    except ObjectDoesNotExist:
        pass
    
    #Verifica produto sugerido
    try:
        Produto.objects.get(suggested=True, nome__iexact=produto.title())
        d['status'] = True
        d['message'] = 'Produto já cadastrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')                    
    except ObjectDoesNotExist:
        pass
            
    d['status'] = False
    d['message'] = 'Produto não existe'
    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
def busca(request):
    d = {}
    
    if request.method == 'POST':
        cidade = request.POST['cidade']
        busca = request.POST['busca']
        ordenar = request.POST['ordenar']
        
        #Verifica termo de pesquisa
        if len(busca) < 3:
            d['status'] = False
            d['message'] = 'Produto com nome muito curto'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
        
        #Verifica cidade
        try:
            cidadeObject = Cidade.objects.get(active=True, id__exact=cidade)
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Cidade não selecionada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Pesquisa produto e ofertas
        try:
            #Lista com as ofertas
            ofertasList = []
            ofertasPromotedList = []
            
            #QuerySet de produtos correspondente a pesquisa
            produtoQuery = Produto.objects.filter(active=True, nome__icontains=busca).order_by('nome')
            if produtoQuery.count() == 0 :
                d['status'] = False
                d['message'] = 'Nenhuma produto encontrado'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
            #Procura ofertas para o QuerySet de produtos
            for produtoObject in produtoQuery:
                #QuerySet de ofertas para o produto (Nao promovidas)
                ofertaQuery = Oferta.active_objects.filter(cidade=cidadeObject, promoted=False, produto=produtoObject).order_by('id')
                if ofertaQuery.count() > 0:
                    #Monta lista de ofertas para o produto
                    for ofertaObject in ofertaQuery:
                        ofertasList.append(ofertaObject)
    
                #QuerySet de ofertas para o produto (Promovidas)
                ofertaQuery = Oferta.active_objects.filter(cidade=cidadeObject, promoted=True, produto=produtoObject).order_by('id')
                if ofertaQuery.count() > 0:
                    #Monta lista de ofertas para o produto
                    for ofertaObject in ofertaQuery:
                        ofertasPromotedList.append(ofertaObject)                    
            
            #Verifica ofertas
            if ( len(ofertasList) +  len(ofertasPromotedList) ) > 0:
                #Funcao para ordenar ofertas
                fSort = None
                if ordenar == 'popularidade':
                    fSort = lambda a,b: cmp(b.get_popularidade(), a.get_popularidade())
                elif ordenar == 'data':
                    fSort = lambda a,b: cmp(b.created, a.created)                
                elif ordenar == 'visualizacoes':
                    fSort = lambda a,b: cmp(b.get_visualizacoes(), a.get_visualizacoes())    
                elif ordenar == 'preco_menor':
                    fSort = lambda a,b: cmp(a.preco, b.preco)
                    
                #Executa ordenacao
                if fSort != None:
                    ofertasList.sort(cmp=fSort)
                    ofertasPromotedList.sort(cmp=fSort)
                    
                #Monta lista unica (insere uma promovida a cada 5 nao promovidas)
                n = 0;
                insert = 5;
                for ofertaObject in ofertasPromotedList:
                    ofertasList.insert(n, ofertaObject);
                    n = n + insert
                
                d['status'] = True
                d['message'] = render_to_string('lista_ofertas.html', RequestContext(request,{'data':ofertasList, 'busca':busca.title(),}) )
                
                #Marca ofertas como buscada em outra thread
                t = OfertaSearchedThread(ofertasList)
                t.start()
                            
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
            else:
                d['status'] = False
                d['message'] = 'Nenhuma oferta encontrada'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
                
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Nenhuma oferta encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')

# Conteudo da oferta para uso em Ajax
def ajax_oferta(request):
    d = {}
    
    oferta_id = request.GET['id']
    
    if request.GET.has_key('next_id'):
        next_id = request.GET['next_id']
    else:
        next_id = None

    if request.GET.has_key('previous_id'):
        previous_id = request.GET['previous_id']
    else:
        previous_id = None
        
    #Verifica se e oferta nova
    try:
        ofertaObject = Oferta.objects.get(active=False, new=True, id__exact=oferta_id)
        d['status'] = False
        d['message'] = 'Oferta cadastrada e em analíse'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
    except ObjectDoesNotExist:
        pass        
    
    #Verifica oferta
    try:
        ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
    except ObjectDoesNotExist:
        d['status'] = False
        d['message'] = 'Oferta não encontrada'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')  
    
    #Verifica se tem mais de uma semana esta como nova
    if ofertaObject.new:
        week_ago = timenow() - datetime.timedelta(days=7)
        if ofertaObject.created < week_ago:
            ofertaObject.new = False
    
    #Verifica se tem mais de um mes e esta como ativa
    if ofertaObject.active:
        month_ago = timenow() - datetime.timedelta(days=30)
        if ofertaObject.created < month_ago:
            ofertaObject.active = False            
            
    #Atualiza viewed
    ofertaObject.viewed = ofertaObject.viewed + 1            
    ofertaObject.save()
                    
    d['status'] = True
    d['message'] = render_to_string('ajax_oferta.html', RequestContext(request,
                                                                       {'oferta':ofertaObject,
                                                                        'produto':ofertaObject.produto,
                                                                        'next_id':next_id,
                                                                        'previous_id':previous_id}))
    d['liked'] = str(ofertaObject.liked)
    d['disliked'] = str(ofertaObject.disliked)

    return HttpResponse(simplejson.dumps(d), mimetype='text/html')

# Conteudo da oferta para ser indexado por robos de busca
def oferta(request): 
    d = {}
    
    if request.GET.has_key('id'):
        oferta_id = request.GET['id']
    else:
        oferta_id = -1

    d['next_id'] = None
    d['previous_id'] = None
        
    #Verifica oferta
    try:
        ofertaObject = Oferta.objects.get(id__exact=oferta_id)
        d['oferta'] = ofertaObject
        d['produto'] = ofertaObject.produto
        d['liked'] = str(ofertaObject.liked)
        d['disliked'] = str(ofertaObject.disliked)
        
        #Verifica se tem mais de uma semana esta como nova
        if ofertaObject.new:
            week_ago = timenow() - datetime.timedelta(days=7)
            if ofertaObject.created < week_ago:
                ofertaObject.new = False
        
        #Verifica se tem mais de um mes e esta como ativa
        if ofertaObject.active:
            month_ago = timenow() - datetime.timedelta(days=30)
            if ofertaObject.created < month_ago:
                ofertaObject.active = False            
                
        #Atualiza viewed
        ofertaObject.viewed = ofertaObject.viewed + 1            
        ofertaObject.save()
    except ObjectDoesNotExist:
        d['oferta'] = None        
        
    context = RequestContext(request)        
    return render_to_response('dialog_oferta.html',
                              d,
                              context_instance=context)

def oferta_shared(request):
    d = {}
            
    if request.method == 'POST':    
        oferta_id = request.POST['id']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:        
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
        #Verifica oferta
        try:
            ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
            ofertaObject.shared = ofertaObject.shared + 1
            ofertaObject.save()
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Oferta não encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Incrementa pontuacao do usuario
        session_user.points = session_user.points + 10
        session_user.save()
        
        #Incrementa pontuacao do criador da oferta
        ofertaObject.user.points = ofertaObject.user.points + 5
        ofertaObject.user.save()
        
        d['status'] = True
        d['message'] = 'Shared registrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    
def oferta_commented(request):
    d = {}
    
    if request.method == 'POST':    
        oferta_id = request.POST['id']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:        
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
        
        #Verifica oferta
        try:
            ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
            ofertaObject.commented = ofertaObject.commented + 1
            ofertaObject.save()        
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Oferta não encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Incrementa pontuacao do usuario
        session_user.points = session_user.points + 20
        session_user.save()
        
        #Incrementa pontuacao do criador da oferta
        ofertaObject.user.points = ofertaObject.user.points + 10
        ofertaObject.user.save()                  
        
        d['status'] = True
        d['message'] = 'Commented registrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    
def busca_shared(request):
    d = {}
            
    if request.method == 'POST':    
        busca = request.POST['busca']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:        
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
        
        #Verifica busca
        #try:
        #    pass
        #except ObjectDoesNotExist:
        #    d['status'] = False
        #    d['message'] = 'Busca não encontrada'
        #    return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Incrementa pontuacao do usuario
        session_user.points = session_user.points + 10
        session_user.save()
        
        d['status'] = True
        d['message'] = 'Shared registrado'
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')

def oferta_like(request):
    d = {}
    
    if request.method == 'POST':    
        oferta_id = request.POST['id']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:        
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
        
        #Verifica cookie
        cookie = '__OpinouOferta__%s' % (oferta_id)
        if request.COOKIES.has_key(cookie):
            d['status'] = False
            d['message'] = 'Desculpe, mas você já opinou nessa oferta!'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')    
    
        #Verifica oferta
        try:
            ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
            ofertaObject.liked = ofertaObject.liked + 1
            ofertaObject.save()
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Oferta não encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Incrementa pontuacao do usuario
        session_user.points = session_user.points + 10
        session_user.save()
        
        #Incrementa pontuacao do criador da oferta
        ofertaObject.user.points = ofertaObject.user.points + 5
        ofertaObject.user.save()

        #Resposta
        d['status'] = True
        d['message'] = 'Like registrado'
        d['liked'] = str(ofertaObject.liked)
        d['disliked'] = str(ofertaObject.disliked)
        response = HttpResponse(simplejson.dumps(d), mimetype='text/html')
        response.set_cookie(str(cookie), True, 7*24*60*60)
        return response
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')    

def oferta_dislike(request):
    d = {}
    
    if request.method == 'POST':    
        oferta_id = request.POST['id']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:        
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'        
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
    
        #Verifica cookie
        cookie = '__OpinouOferta__%s' % (oferta_id)
        if request.COOKIES.has_key(cookie):
            d['status'] = False
            d['message'] = 'Desculpe, mas você já opinou nessa oferta!'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
        #Verifica oferta
        try:
            ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
            ofertaObject.disliked = ofertaObject.disliked + 1
            ofertaObject.save()
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Oferta não encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Incrementa pontuacao do usuario
        session_user.points = session_user.points + 10
        session_user.save()
        
        #Decrementa pontuacao do criador da oferta
        ofertaObject.user.points = ofertaObject.user.points - 5
        ofertaObject.user.save()                  
         
        #Resposta    
        d['status'] = True
        d['message'] = 'Dislike registrado'
        d['liked'] = str(ofertaObject.liked)
        d['disliked'] = str(ofertaObject.disliked)
        response = HttpResponse(simplejson.dumps(d), mimetype='text/html')
        response.set_cookie(str(cookie), True, 7*24*60*60)
        return response
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')

def oferta_notify(request):
    d = {}
    d.update(csrf(request))
    
    user_id = request.GET['uid']
    produto_id = request.GET['pid']
    value = request.GET['value']
    
    try:
        userObject = Usuario.objects.get(id__exact=user_id)
        produtoObject = Produto.objects.get(id__exact=produto_id)
        ofertaQuery = produtoObject.ofertas.filter(user=userObject)
        for ofertaObject in ofertaQuery:
            if value == "0":
                ofertaObject.notify = False
            else:
                ofertaObject.notify = True
            ofertaObject.save()
        d['status'] = True
        d['info'] = 'Notificações alteradas com sucesso' 
    except ObjectDoesNotExist:
        d['status'] = False
        d['info'] = 'Usuario e/ou produto não encontrado'
    
    context = RequestContext(request)        
    return render_to_response('dialog_show_info.html',
                              d,
                              context_instance=context)        
    
def local_searched(request):
    d = {}
    
    if request.method == 'POST':    
        local_id = request.POST['id']
        
        #Verifica local
        try:
            localObject = Local.objects.get(id__exact=local_id)
            localObject.searched = localObject.searched + 1
            localObject.save()
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Local não encontrado'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')  
        
        d['status'] = True
        d['message'] = 'Shared registrado'
        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')        

def dialog_add_oferta(request):
    d = {}
    context = RequestContext(request)        
    return render_to_response('dialog_add_oferta.html',
                              d,
                              context_instance=context)

def add_oferta(request):
    d = {}
    
    if request.method == 'POST':    
        user_id = request.POST['user_id']
        cidade = request.POST['cidade']
        produto = request.POST['produto']
        local = request.POST['local']
        preco = request.POST['preco']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')    
                
        #Verifica usuario
        try:
            userObject = Usuario.objects.get(id=user_id)
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Usuário não existe'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Verifica se esta tentando cadastrar oferta como outro usuario
        if userObject != session_user:
            d['status'] = False
            d['message'] = 'Acesso a cadastro de oferta negado'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Verifica cidade
        try:
            cidadeObject = Cidade.objects.get(active=True, id__exact=cidade)
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Cidade não selecionada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Verifica produto ativo
        try:
            produtoObject = Produto.objects.get(active=True, nome__iexact=produto.title())            
        except ObjectDoesNotExist:
            #Verifica produto sugerido
            try:
                produtoObject = Produto.objects.get(suggested=True, nome__iexact=produto.title())            
            except ObjectDoesNotExist:
                #Marca para criar novo produto
                produtoObject = None
                
        #Verifica local
        try:
            localObject = Local.objects.get(active=True, nome__iexact=local.title())
        except ObjectDoesNotExist:
            #Marca para criar novo local
            localObject = None                              

        #Verifica preco
        try:
            f = atof(preco)
            decimalPreco = Decimal(str(f))
        except (ValueError, InvalidOperation):
            d['status'] = False
            d['message'] = 'Entre com um preço válido'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
        #Criar novo local
        if localObject == None:
            #Verifica tamanho do local
            if len(local) < 3:
                d['status'] = False
                d['message'] = 'Local com nome muito curto'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                                
            #Cria novo local
            localObject = Local.objects.create(nome=local.title())
            
            #Salva local
            localObject.save()
        
        #Criar novo produto
        if produtoObject == None:
            #Verifica tamanho do nome do produto
            if len(produto) < 3:
                d['status'] = False
                d['message'] = 'Produto com nome muito curto'
                return HttpResponse(simplejson.dumps(d), mimetype='text/html')
                        
            #Cria produto novo
            produtoObject = Produto.objects.create(nome=produto.title(),
                                                   suggested=True)
            #Salva produto novo
            produtoObject.save()
            
            #Envia email de produto adicionado
            t1 = SendSuggestProdutoThread(request, produtoObject)
            t1.start()            
                
        #Cria nova oferta
        ofertaObject = Oferta.objects.create(produto=produtoObject,
                                             user=userObject,
                                             cidade=cidadeObject,
                                             local=localObject,
                                             preco=decimalPreco)
        
        #Salva nova oferta
        ofertaObject.save()
        
        #Incrementa pontuacao do usuario
        userObject.points = userObject.points + 100
        userObject.save()
        
        #Envia email de oferta adicionada
        t2 = SendAddOfertaThread(request, ofertaObject, userObject, cidadeObject)
        t2.start()
         
        d['status'] = True
        d['message'] = 'Oferta cadastrada com sucesso'
        d['oferta_id'] = ofertaObject.id
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
        
def dialog_report_oferta(request):
    d = {}
    
    oferta_id = request.GET['id']
    
    #Verifica oferta
    try:
        ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
        d['oferta'] = ofertaObject
    except ObjectDoesNotExist:
        d['oferta'] = None
        
    d['choices'] = ErroOferta.CODIGOS_ERRO
        
    context = RequestContext(request)        
    return render_to_response('dialog_report_oferta.html',
                              d,
                              context_instance=context)
    
def report_oferta(request):
    d = {}

    if request.method == 'POST':
        oferta_id = request.POST['oferta_id']    
        user_id = request.POST['user_id']
        cod_erro = request.POST['erro']
        
        #Verifica se esta logado
        session_user = get_session_user(request)
        if session_user == None:
            d['status'] = False
            d['message'] = 'Entre ou registre-se no site primeiro'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')        
    
        #Verifica cookie
        cookie = '__ReportouErroOferta__%s' % (oferta_id)
        if request.COOKIES.has_key(cookie):
            d['status'] = False
            d['message'] = 'Desculpe, mas você já informou erro para essa oferta'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
        
        #Verifica usuario
        try:
            userObject = Usuario.objects.get(id=user_id)
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Usuário não existe'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
            
        #Verifica oferta
        try:
            ofertaObject = Oferta.active_objects.get(id__exact=oferta_id)
        except ObjectDoesNotExist:
            d['status'] = False
            d['message'] = 'Oferta não encontrada'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')
       
        #Cria novo erro da oferta
        erro_oferta = ErroOferta.objects.create(oferta=ofertaObject,
                                                user=userObject,
                                                erro=cod_erro)
    
        #Salva erro da oferta
        erro_oferta.save()
        
        #Incrementa pontuacao do usuario
        userObject.points = userObject.points + 20
        userObject.save()
        
        #Decrementa pontuacao do criador da oferta
        ofertaObject.user.points = ofertaObject.user.points - 20
        ofertaObject.user.save()        
                
        #Envia email de erro da oferta reportado
        t = SendErroOfertaThread(request, ofertaObject, erro_oferta)
        t.start()        
        
        #Verifica numero de erros da oferta
        if ofertaObject.get_erros() > 5:
            #Desativa oferta
            ofertaObject.active = False
            ofertaObject.save()
            d['status'] = True
            d['message'] = 'Obrigado! Oferta desativada por exceder limite de erros registrados'
            return HttpResponse(simplejson.dumps(d), mimetype='text/html')            
        
        d['status'] = True
        d['message'] = 'Obrigado! Erro da oferta registrado com sucesso'    
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    else:
        d['status'] = False
        d['message'] = 'Falha no envio do formulário'        
        return HttpResponse(simplejson.dumps(d), mimetype='text/html')
    