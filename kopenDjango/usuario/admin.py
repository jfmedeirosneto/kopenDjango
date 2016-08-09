#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.contrib import admin

from kopenDjango.usuario.models import Usuario
from kopenDjango.produto.models import Oferta, ErroOferta

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
    
class UsuarioAdmin(admin.ModelAdmin):
    readonly_fields = ('password_hash', 'points')
    list_display = ('user', 'name', 'email', 'active', 'points', 'created', 'modified')
    list_display_links = ['user']
    list_filter = ['active']
    search_fields = ('user', 'nome', 'email')    
    inlines = [OfertasInline, OfertasErroInline]
    actions = ('ativar', 'desativar')
    
    def ativar(self, request, queryset):
        for userObject in queryset:
            userObject.active = True
            userObject.failures = 0
            userObject.save()
    ativar.short_description = "Ativar Usuários selecionadas"

    def desativar(self, request, queryset):
        for userObject in queryset:
            userObject.active = False
            userObject.save()
    desativar.short_description = "Desativar Usuários selecionadas"        

admin.site.register(Usuario, UsuarioAdmin);