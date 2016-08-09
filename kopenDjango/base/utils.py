#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import os, string, random, unicodedata, time
from HTMLParser import HTMLParser
from threading import Thread

from hashlib import sha224

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from kopenDjango.base.mailer import Mailer
from kopenDjango.base.mailer import Message

from kopenDjango.settings import MEDIA_ROOT, SECRET_KEY, DEBUG

KOPEN_WEBVIEW_USER_AGENT = 'kopenDjango-WebView-User-Agent-1ePaIY4s'
        
# Funcao para setar webview
def set_session_webview(request):
    request.session[KOPEN_WEBVIEW_USER_AGENT] = True

# Funcao para remover webview
def delete_session_webview(request):
    try:
        del request.session[KOPEN_WEBVIEW_USER_AGENT]
    except KeyError:
        pass    
    
# Funcao para retornar webview
def get_session_webview(request):
    if request.session.get(KOPEN_WEBVIEW_USER_AGENT):
        return request.session[KOPEN_WEBVIEW_USER_AGENT]
    else:
        return False    

# Funcao now em funcao do timezone configurado no django
def timenow():
    return timezone.localtime(timezone.now())

# Gera string aleatoria
def get_random_string(length):
    return ''.join(map(lambda x: random.choice(string.ascii_letters + string.digits), range(length)))    

# Parser das imagens
class ImgHTMLParser(HTMLParser):
    images = {}
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'img' :
            for name, value in attrs:
                if name.lower() == 'src':
                    cid = 'image' + str( len(self.images)+1 )
                    self.images[cid] = value
    
    def get_images(self):
        return self.images

# Remove acentos
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
     
# Funcao geral para enviar email    
def send_email(request, sender, receiver, subject, html_body):
    # Acerto da data do email
    # Hoje = Date: Sex, 04 Out 2013 03:39:39 +0000 (assim faz pelo locale pt_BR)
    # Correto = Date: Sat, 24 Nov 2035 11:45:15 −0500 (assim eh o padrao para headers do email)
    weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    t = time.gmtime()
    mon = t[1]
    mday = t[2]
    wday = t[6]
    date = "%s, %d %s %s -0000" % (weekdays[wday], mday, months[mon-1], time.strftime("%Y %H:%M:%S", t))
    
    # Cria mensagem
    message = Message(From=remove_accents(sender),
                      To=remove_accents(receiver),
                      Date=date,
                      charset='utf-8')
    
    # Request Context
    context = RequestContext(request)
    
    # Subject do email
    message.Subject = str( subject + " " + context.get("site_name", "") )
    
    # Gera mensagem em html
    html = render_to_string('emails/base_email.html',
                            {'html_body':html_body,},
                            context_instance=context)
    
    # Parser das imagens no html para anexar ao email
    parser = ImgHTMLParser()
    parser.feed(html)
    images = parser.get_images()
    for cid, image_name in images.items():
        # Adiciona a mensagem como inline (cid)
        image_file = os.path.join(MEDIA_ROOT, image_name)
        message.attach(image_file, cid=cid)
        # Troca no arquivo pelo cid
        old = "src=\"" + image_name + "\""
        new = "src=\"cid:" + cid + "\""
        html = html.replace(old, new)
    
    # Mensagem em html e texto
    message.Html = html
    message.Body = strip_tags(html_body)
   
    # Envia mensagem
    if DEBUG:
        sender = Mailer('localhost')
    else:
        sender = Mailer('mail.ofertasqui.com.br', '25', False, 'admin@ofertasqui.com.br', 'anjinho04')
    sender.send(message)

# Envia email que nova oferta foi adicionada
class SendAddOfertaThread(Thread):
    def __init__ (self, request, ofertaObject, userObject, cidadeObject):
        Thread.__init__(self)
        self.request = request
        self.ofertaObject = ofertaObject
        self.userObject = userObject
        self.cidadeObject = cidadeObject
        
    def run(self):
        context = RequestContext(self.request)
        
        #Email com link da aministracao da oferta
        admin_name = context.get('admin_name', 'kopenDjango')
        admin_email = context.get('admin_email', 'kopen@kopen.mobi')                
        html_body = render_to_string('emails/admin_add_oferta_email.html',
                                     {'oferta':self.ofertaObject,
                                      'receiver':admin_name},
                                     context)
        sender = ("%s <%s>") % (admin_name, admin_email)
        receiver = ("%s <%s>") % (admin_name, admin_email)
        send_email(self.request,
                   sender,
                   receiver,
                   'Nova Oferta Adicionada',
                   html_body)
        
        if self.userObject:
            #Email para usuario
            user_name = self.userObject.name
            user_email = self.userObject.email            
            html_body = render_to_string('emails/add_oferta_email.html',
                                         {'oferta':self.ofertaObject,
                                          'receiver':user_name},
                                         context)
            sender = ("%s <%s>") % (admin_name, admin_email)
            receiver = ("%s <%s>") % (user_name, user_email)
            send_email(self.request,
                       sender,
                       receiver,
                       'Nova Oferta Adicionada',
                       html_body)
            
            #Email para admin       
            html_body = render_to_string('emails/add_oferta_email.html',
                                         {'oferta':self.ofertaObject,
                                          'receiver':admin_name},
                                         context)            
            sender = ("%s <%s>") % (user_name, user_email)
            receiver = ("%s <%s>") % (admin_name, admin_email)
            send_email(self.request,
                       sender,
                       receiver,
                       'Nova Oferta Adicionada',
                       html_body)
            
        #Lista com os usuarios com ofertas relacionadas ao produto dessa oferta
        relatedUsers = []
        produtoObject = self.ofertaObject.produto
        relatedOfertas = produtoObject.ofertas.filter(cidade=self.cidadeObject,notify=True)
        relatedOfertas = relatedOfertas.exclude(user=self.userObject)
        for relatedOfertaObject in relatedOfertas:
            if relatedOfertaObject.user not in relatedUsers:
                relatedUsers.append(relatedOfertaObject.user)
        for relatedUserObject in relatedUsers:
            #Envia email par usuarios relacionados
            user_name = relatedUserObject.name
            user_email = relatedUserObject.email            
            html_body = render_to_string('emails/related_add_oferta_email.html',
                                         {'oferta':self.ofertaObject,
                                          'user':relatedUserObject,
                                          'produto':produtoObject,
                                          'receiver':user_name},
                                         context)
            sender = ("%s <%s>") % (admin_name, admin_email)
            receiver = ("%s <%s>") % (user_name, user_email)
            send_email(self.request,
                       sender,
                       receiver,
                       'Nova Oferta Adicionada',
                       html_body)                              
            
# Envia email que nova oferta foi adicionada
class SendSuggestProdutoThread(Thread):
    def __init__ (self, request, produtoObject):
        Thread.__init__(self)
        self.request = request
        self.produtoObject = produtoObject
        
    def run(self):
        context = RequestContext(self.request)
        admin_name = context.get('admin_name', 'kopenDjango')
        admin_email = context.get('admin_email', 'kopen@kopen.mobi')                
        html_body = render_to_string('emails/admin_suggest_produto_email.html',
                                     {'produto':self.produtoObject,
                                      'receiver':admin_name},
                                     context)
        sender = ("%s <%s>") % (admin_name, admin_email)
        receiver = ("%s <%s>") % (admin_name, admin_email)
        send_email(self.request,
                   sender,
                   receiver,
                   'Novo Produto Sugerido',
                   html_body)
        
# Envia email que novo erro da oferta foi reportado
class SendErroOfertaThread(Thread):
    def __init__ (self, request, ofertaObject, erro_oferta):
        Thread.__init__(self)
        self.request = request
        self.ofertaObject = ofertaObject
        self.erro_oferta= erro_oferta
        
    def run(self):
        context = RequestContext(self.request)
        admin_name = context.get('admin_name', 'kopenDjango')
        admin_email = context.get('admin_email', 'kopen@kopen.mobi')                
        html_body = render_to_string('emails/admin_erro_oferta_email.html',
                                     {'oferta':self.ofertaObject,
                                      'erro_oferta':self.erro_oferta,
                                      'receiver':admin_name},
                                     context)
        sender = ("%s <%s>") % (admin_name, admin_email)
        receiver = ("%s <%s>") % (admin_name, admin_email)
        send_email(self.request,
                   sender,
                   receiver,
                   'Erro da Oferta Reportado',
                   html_body)        

# Envia email que nova oferta foi adicionada
class SendRequestPasswordThread(Thread):
    def __init__ (self, request, userObject):
        Thread.__init__(self)
        self.request = request
        self.userObject = userObject
        
    def run(self):
        if self.userObject:        
            #Gera Hash para gerar link de recuperar senha
            password_hash = sha224(SECRET_KEY + self.userObject.email + unicode(timenow())).hexdigest()
            user_name = self.userObject.name
            user_email = self.userObject.email                            
            context = RequestContext(self.request)
            html_body = render_to_string('emails/request_password_email.html',
                                         {'user_id':self.userObject.id,
                                          'password_hash':password_hash,
                                          'receiver': user_name},
                                         context)
            admin_name = context.get('admin_name', 'kopenDjango')
            admin_email = context.get('admin_email', 'kopen@kopen.mobi')
            sender = ("%s <%s>") % (admin_name, admin_email)
            receiver = ("%s <%s>") % (user_name, user_email)
            send_email(self.request,
                       sender,
                       receiver,
                       'Esqueceu sua Senha',
                       html_body)
        
            #Salva password hash nos dados do usuario
            self.userObject.password_hash = password_hash
            self.userObject.save()
        
# Envia email de fale conosco
class SendContactFormThread(Thread):
    def __init__ (self, request, nome, email, mensagem):
        Thread.__init__(self)
        self.request = request
        self.nome = nome
        self.email = email
        self.mensagem = "<br/>".join(mensagem.split("\n"))
        
    def run(self):
        context = RequestContext(self.request)
        admin_name = context.get('admin_name', 'kopenDjango')
        admin_email = context.get('admin_email', 'kopen@kopen.mobi')                
        html_body = render_to_string('emails/admin_contact_form.html',
                                     {'nome':self.nome,
                                      'email':self.email,
                                      'mensagem':self.mensagem,
                                      'receiver':admin_name},
                                     context)
        sender = ("%s <%s>") % (self.nome, self.email)
        receiver = ("%s <%s>") % (admin_name, admin_email)
        send_email(self.request,
                   sender,
                   receiver,
                   'Novo Contato Fale Conosco',
                   html_body)        