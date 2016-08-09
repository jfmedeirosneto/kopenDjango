#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.db import models

import random, datetime

from kopenDjango.stdimage.fields import StdImageField
from kopenDjango.usuario.models import Usuario
from kopenDjango.cidade.models import Cidade
from kopenDjango.base.utils import timenow

class Produto(models.Model):
    nome = models.CharField('Nome',
                            max_length=140,
                            help_text=u'Nome do produto.')
    imagem = StdImageField('Imagem',
                           size=(220, 220),
                           thumbnail_size=(50, 50),
                           upload_to='produto',
                           blank=True,
                           null=True,
                           help_text=u'Imagem do produto.')
    active = models.BooleanField('Ativo',
                                 default=True,
                                 help_text=u'Produto ativo.')
    suggested = models.BooleanField('Sugerido',
                                    default=False,
                                    help_text=u'Produto ativo.')
    created = models.DateTimeField('Criado',
                                   default=timenow)
    modified = models.DateTimeField('Modificado',
                                    default=timenow)
        
    def save(self, *args, **kwargs):
        self.nome = self.nome.title()
        self.modified = timenow()
        super(Produto, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.nome    
    
    class Meta:
        verbose_name = u'Produto'
        verbose_name_plural = u'Produtos'
        ordering = ['nome']
        
class Local(models.Model):
    nome = models.CharField('Nome',
                            max_length=140,
                            help_text=u'Nome do local.')
    imagem = StdImageField('Imagem',
                           size=(220, 220),
                           thumbnail_size=(50, 50),
                           upload_to='local',
                           blank=True,
                           null=True,
                           help_text=u'Imagem do local.')
    active = models.BooleanField('Ativo',
                                 default=True,
                                 help_text=u'Local ativo.')
    searched = models.DecimalField('Searched',
                                   max_digits=12,
                                   decimal_places=0,
                                   default=0,
                                   help_text=u'Número de buscas.')    
    created = models.DateTimeField('Criado',
                                   default=timenow)
    modified = models.DateTimeField('Modificado',
                                    default=timenow)
        
    def save(self, *args, **kwargs):
        self.nome = self.nome.title()
        self.modified = timenow()
        super(Local, self).save(*args, **kwargs)

    def get_popularidade(self):
        value = self.searched
        ofertaQuery = self.ofertas.filter(active=True);
        if ofertaQuery.count() > 0:
            value = value + ofertaQuery.count()
            for ofertaObject in ofertaQuery:
                value = value + ofertaObject.get_popularidade()
        return int(value)
    get_popularidade.short_description = 'Popularidade'   
    
    def __unicode__(self):
        return self.nome    
    
    class Meta:
        verbose_name = u'Local'
        verbose_name_plural = u'Locais'
        ordering = ['nome']        

class OfertaActiveManager(models.Manager):
    def get_query_set(self):
        #Retorna query ja tratado
        month_ago = timenow() - datetime.timedelta(days=30)
        return super(OfertaActiveManager, self).get_query_set().\
            filter(active=True,
                   produto__active=True,
                   user__active=True,
                   local__active=True).\
            exclude(created__lt=month_ago)
     
class Oferta(models.Model):
    produto = models.ForeignKey(Produto,
                                help_text=u'Produto da oferta.',
                                related_name='ofertas')
    user = models.ForeignKey(Usuario,
                             help_text=u'Usuário que criou a oferta.',
                             related_name='ofertas')
    cidade = models.ForeignKey(Cidade,
                               help_text=u'Cidade da oferta.',
                               related_name='ofertas')    
    local = models.ForeignKey(Local,
                              help_text=u'Local da oferta.',
                              related_name='ofertas')
    imagem = StdImageField('Imagem',
                           size=(220, 220),
                           thumbnail_size=(50, 50),
                           upload_to='oferta',
                           blank=True,
                           null=True,                               
                           help_text=u'Imagem da oferta.')        
    preco = models.DecimalField('Preço',
                                max_digits=7,
                                decimal_places=3,
                                help_text=u'Preço normal do produto.')    
    active = models.BooleanField('Ativo',
                                 default=True,
                                 help_text=u'Oferta ativa.')
    promoted = models.BooleanField('Promovida',
                                   default=False,
                                   help_text=u'Oferta de anunciante.')
    new = models.BooleanField('Nova',
                              default=True,
                              help_text=u'Oferta nova.')
    notify = models.BooleanField('Notifica',
                                 default=True,
                                 help_text=u'Notifica usuário.')    
    shared = models.DecimalField('Shared',
                                 max_digits=12,
                                 decimal_places=0,
                                 default=0,                               
                                 help_text=u'Número de compartilhamentos.')
    commented = models.DecimalField('Commented',
                                    max_digits=12,
                                    decimal_places=0,
                                    default=0,
                                    help_text=u'Número de comentários.')    
    liked = models.DecimalField('Liked',
                                max_digits=12,
                                decimal_places=0,
                                default=0,
                                help_text=u'Número de gostaram.')
    disliked = models.DecimalField('Disliked',
                                   max_digits=12,
                                   decimal_places=0,
                                   default=0,
                                   help_text=u'Número de não gostaram.')  
    searched = models.DecimalField('Searched',
                                   max_digits=12,
                                   decimal_places=0,
                                   default=0,
                                   help_text=u'Número de buscas.')
    viewed = models.DecimalField('Viewed',
                                 max_digits=12,
                                 decimal_places=0,
                                 default=0,
                                 help_text=u'Número de visualizações.')    
    created = models.DateTimeField('Criado',
                                   default=timenow)
    modified = models.DateTimeField('Modificado',
                                    default=timenow)

    objects = models.Manager() #Default manager (deve ser o primeiro para nao gerar erro ao salvar objeto)
    active_objects = OfertaActiveManager() #Filtra ativos
   
    def get_imagem_url(self):
        if self.imagem:
            return self.imagem.url
        elif self.produto.imagem:
            return self.produto.imagem.url
        else:
            return "/static/sem_imagem.png"
            
    def get_thumb_imagem_url(self):
        if self.imagem:
            return self.imagem.thumbnail.url()
        elif self.produto.imagem:
            return self.produto.imagem.thumbnail.url()
        else:
            return "/static/sem_imagem.thumbnail.png"
        
    def get_imagem_width(self):
        if self.imagem:
            return self.imagem.width
        elif self.produto.imagem:
            return self.produto.imagem.width
        else:
            return 80        
        
    def get_imagem_height(self):
        if self.imagem:
            return self.imagem.height
        elif self.produto.imagem:
            return self.produto.imagem.height
        else:
            return 80        
        
    def get_thumb_imagem_width(self):
        h_factor = 50.0/self.get_imagem_width()
        v_factor = 50.0/self.get_imagem_height()
        factor = min(h_factor, v_factor)
        if self.imagem:
            return int(factor*self.imagem.width)
        elif self.produto.imagem:
            return int(factor*self.produto.imagem.width)
        else:
            return 50        
        
    def get_thumb_imagem_height(self):
        h_factor = 50.0/self.get_imagem_width()
        v_factor = 50.0/self.get_imagem_height()
        factor = min(h_factor, v_factor)        
        if self.imagem:
            return int(factor*self.imagem.height)
        elif self.produto.imagem:
            return int(factor*self.produto.imagem.height)
        else:
            return 50        
    
    def get_popularidade(self):
        value = self.shared + self.commented + self.liked - self.disliked
        return int(value)
    get_popularidade.short_description = 'Popularidade'    
    
    def get_visualizacoes(self):
        value = self.viewed 
        return int(value)
    get_visualizacoes.short_description = 'Visualizações'
    
    def get_erros(self):
        return self.erros.filter(resolved=False).count()
    get_erros.short_description = 'Erros'        

    def selflink(self):
        if self.id:
            return "<a href='/admin/produto/oferta/%s/' target='_blank'>Editar Oferta</a>" % str(self.id)
        else:
            return "---"
    selflink.allow_tags = True
    selflink.short_description = 'Admin Link'

    def save(self, *args, **kwargs):
        self.modified = timenow()
        super(Oferta, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return u'%s - %s' % (self.produto, self.local)    
    
    class Meta:
        verbose_name = u'Oferta'
        verbose_name_plural = u'Ofertas'
        ordering = ['produto']
        
        
class ErroOferta(models.Model):
    oferta = models.ForeignKey(Oferta,
                               help_text=u'Oferta com erro.',
                               related_name='erros')
    user = models.ForeignKey(Usuario,
                             help_text=u'Usuário que reportou o erro.',
                             related_name='erros')
    CODIGOS_ERRO = (
        (1, 'Preço errado'),
        (2, 'Local não vende produto'),
        (3, 'Oferta enganosa'),
        (4, 'Spam ou fraude'),
    )
    erro = models.DecimalField('Erro',
                                max_digits=2,
                                decimal_places=0,
                                default=0,
                                choices=CODIGOS_ERRO,
                                help_text=u'Código do erro.')
    new = models.BooleanField('Novo',
                              default=True,
                              help_text=u'Erro novo.')        
    resolved = models.BooleanField('Resolvido',
                              default=False,
                              help_text=u'Erro resolvido.')    
    created = models.DateTimeField('Criado',
                                   default=timenow)
    modified = models.DateTimeField('Modificado',
                                    default=timenow)
        
    def save(self, *args, **kwargs):
        self.modified = timenow()
        super(ErroOferta, self).save(*args, **kwargs)
        
    def selflink(self):
        if self.id:
            return "<a href='/admin/produto/errooferta/%s/' target='_blank'>Editar Erro da Oferta</a>" % str(self.id)
        else:
            return "---"
    selflink.allow_tags = True
    selflink.short_description = 'Admin Link'        
        
    def __unicode__(self):
        return u'%s - %s' % (self.oferta, self.get_erro_display())        
                
    class Meta:
        verbose_name = u'Erro Oferta'
        verbose_name_plural = u'Erros Oferta'
        ordering = ['oferta']                

#Retorna lista de destaques
def destaques_popular():
    #Ofertas nao promovidas e promovidas
    ofertasList = list(Oferta.active_objects.filter(promoted=False))
    ofertasPromotedList = list(Oferta.active_objects.filter(promoted=True))
    
    #Ordena por popularidade
    fSort = lambda a,b: cmp(b.get_popularidade(), a.get_popularidade())
    ofertasList.sort(cmp=fSort)
    ofertasPromotedList.sort(cmp=fSort)
    
    #Monta lista unica (insere uma promovida a cada 5 nao promovidas)
    n = 0;
    insert = 5;
    for ofertaObject in ofertasPromotedList:
        ofertasList.insert(n, ofertaObject);
        n = n + insert
        
    return ofertasList

#Retorna lista randomica de destaques
def destaques_random():
    #Ofertas nao promovidas e promovidas
    ofertasList = list(Oferta.active_objects.filter(promoted=False))
    ofertasPromotedList = list(Oferta.active_objects.filter(promoted=True))
    
    #Ordena randomicamente
    random.shuffle(ofertasList)
    random.shuffle(ofertasPromotedList)
    
    #Monta lista unica (insere uma promovida a cada 5 nao promovidas)
    n = 0;
    insert = 5;
    for ofertaObject in ofertasPromotedList:
        ofertasList.insert(n, ofertaObject);
        n = n + insert
    
    fSort = lambda a,b: cmp(b.get_popularidade(), a.get_popularidade())
    ofertasList.sort(cmp=fSort)
    
    return ofertasList