#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import datetime

from django.contrib import admin
from django.db import models

from kopenDjango.produto.models import Produto, Local, Oferta, ErroOferta
from kopenDjango.produto.widgets import MyAdminImageWidget
from kopenDjango.base.utils import timenow

class OfertasInline(admin.TabularInline):
    model = Oferta
    can_delete = False
    extra = 0
    editable_fields = []    
    fields = ('selflink', 'user', 'cidade', 'local', 'preco', 'active', 'new')
    readonly_fields = fields
    
    def has_add_permission(self, request):
        return False

class OfertasErroInline(admin.TabularInline):
    model = ErroOferta
    can_delete = False
    extra = 0
    editable_fields = []    
    fields = ('selflink', 'user', 'erro', 'resolved', 'new')
    readonly_fields = fields
    
    def has_add_permission(self, request):
        return False
        
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'active', 'suggested', 'created', 'modified')
    list_display_links = ['nome']
    list_filter = ('active', 'suggested')
    search_fields = ['nome']
    readonly_fields = ('created', 'modified')
    inlines = [OfertasInline]    
    formfield_overrides = { models.ImageField: {'widget': MyAdminImageWidget()} }
    actions = ('ativar', 'desativar')
    
    def ativar(self, request, queryset):
        for produtoObject in queryset:
            produtoObject.active = True
            produtoObject.save()
    ativar.short_description = "Ativar Produtos selecionadas"

    def desativar(self, request, queryset):
        for produtoObject in queryset:
            produtoObject.active = False
            produtoObject.save()
    desativar.short_description = "Desativar Produtos selecionadas"        
    
class LocalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'active', 'created', 'modified', 'searched', 'get_popularidade')
    list_display_links = ['nome']
    list_filter = ['active']
    search_fields = ['nome']
    readonly_fields = ('created', 'modified', 'searched')
    inlines = [OfertasInline]    
    formfield_overrides = { models.ImageField: {'widget': MyAdminImageWidget()} }
    actions = ('ativar', 'desativar', 'zerar_contadores')
    
    def ativar(self, request, queryset):
        for localObject in queryset:
            localObject.active = True
            localObject.save()
    ativar.short_description = "Ativar Locais selecionadas"

    def desativar(self, request, queryset):
        for localObject in queryset:
            localObject.active = False
            localObject.save()
    desativar.short_description = "Desativar Locais selecionadas"
    
    def zerar_contadores(self, request, queryset):
        for localObject in queryset:
            localObject.searched = 0
            localObject.save()
    zerar_contadores.short_description = "Zerar contadores dos locais selecionadas"        
    
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'preco', 'user', 'cidade', 'local', 'active', 'promoted', 'new', 'get_popularidade', 'get_erros', 'created', 'modified')
    list_display_links = ['produto']
    list_filter = ('active', 'promoted', 'new', 'user', 'cidade')
    search_fields = ('produto__nome', 'cidade__nome', 'local', 'user__user', 'user__name', 'user__email')
    readonly_fields = ('created', 'modified', 'shared', 'commented', 'liked', 'disliked', 'searched', 'viewed')
    inlines = [OfertasErroInline]            
    formfield_overrides = { models.ImageField: {'widget': MyAdminImageWidget()} }
    actions = ('ativar', 'desativar', 'desmarcar_nova', 'zerar_contadores', 'verificar_datas')

    def ativar(self, request, queryset):
        for ofertaObject in queryset:
            ofertaObject.active = True
            ofertaObject.new = False
            ofertaObject.save()
    ativar.short_description = "Ativar ofertas selecionadas"

    def desativar(self, request, queryset):
        for ofertaObject in queryset:
            ofertaObject.active = False
            ofertaObject.new = False
            ofertaObject.save()
    desativar.short_description = "Desativar ofertas selecionadas"
    
    def desmarcar_nova(self, request, queryset):
        for ofertaObject in queryset:
            ofertaObject.new = False
            ofertaObject.save()
    desmarcar_nova.short_description = "Desmarcar Nova ofertas selecionadas"    
            
    def zerar_contadores(self, request, queryset):
        for ofertaObject in queryset:
            ofertaObject.shared = 0
            ofertaObject.commented = 0
            ofertaObject.liked = 0
            ofertaObject.disliked = 0
            ofertaObject.searched = 0
            ofertaObject.viewed = 0
            ofertaObject.save()
    zerar_contadores.short_description = "Zerar contadores das ofertas selecionadas"
    
    def verificar_datas(self, request, queryset):
        #Desativa ofertas antigas
        month_ago = timenow() - datetime.timedelta(days=30)
        newQueryset = queryset.filter(created__lt=month_ago)
        for ofertaObject in newQueryset:
            ofertaObject.active = False
            ofertaObject.save()
        #Desmarca nova ofertas antigas
        week_ago = timenow() - datetime.timedelta(days=7)
        newQueryset = queryset.filter(created__lt=week_ago)
        for ofertaObject in newQueryset:
            ofertaObject.new = False
            ofertaObject.save()   
    verificar_datas.short_description = "Verifica datas das ofertas selecionadas"

class ErroOfertaAdmin(admin.ModelAdmin):
    list_display = ('oferta', 'user', 'erro', 'new', 'resolved', 'created', 'modified')
    list_display_links = ['oferta']
    list_filter = ('new', 'resolved', 'erro')
    search_fields = ('oferta__produto__nome', 'oferta__local', 'user__user', 'user__name')
    readonly_fields = ('created', 'modified')
    actions = ['resolvida']
    
    def resolvida(self, request, queryset):
        for erroObject in queryset:
            erroObject.resolved = True
            erroObject.new = False
            erroObject.save()
    resolvida.short_description = "Erros selecionados resolvidos"

admin.site.register(Produto, ProdutoAdmin);
admin.site.register(Local, LocalAdmin);
admin.site.register(Oferta, OfertaAdmin);
admin.site.register(ErroOferta, ErroOfertaAdmin);