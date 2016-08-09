#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.conf.urls import patterns, include
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^kopenDjango/', include('kopenDjango.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),    
    
    # Index
    (r'^$', 'kopenDjango.base.views.index'),
    (r'^noscript/$', 'kopenDjango.base.views.noscript'),    
    (r'^dialog_contact_form/$', 'kopenDjango.base.views.dialog_contact_form'),
    (r'^contact_form/$', 'kopenDjango.base.views.contact_form'),
    
    # Links usuario
    (r'^dialog_change_user/$', 'kopenDjango.usuario.views.dialog_change_user'),
    (r'^dialog_user_points/$', 'kopenDjango.usuario.views.dialog_user_points'),
    (r'^dialog_top_users/$', 'kopenDjango.usuario.views.dialog_top_users'),
    (r'^dialog_login/$', 'kopenDjango.usuario.views.dialog_login'),
    (r'^dialog_request_password/$', 'kopenDjango.usuario.views.dialog_request_password'),
    (r'^dialog_register_user/$', 'kopenDjango.usuario.views.dialog_register_user'),
    (r'^dialog_change_password/(?P<user_id>\d+)/(?P<password_hash>[0-9a-f]+)/$', 'kopenDjango.usuario.views.dialog_change_password'),    
    (r'^dialog_termos_uso/$', 'kopenDjango.usuario.views.dialog_termos_uso'),
    (r'^login/$', 'kopenDjango.usuario.views.login'),    
    (r'^request_password/$', 'kopenDjango.usuario.views.request_password'),
    (r'^logout/$', 'kopenDjango.usuario.views.logout'),        
    (r'^register/$', 'kopenDjango.usuario.views.register'),
    (r'^change_user/$', 'kopenDjango.usuario.views.change_user'),
    (r'^change_password/$', 'kopenDjango.usuario.views.change_password'),
    (r'^facebook_authorize/$', 'kopenDjango.usuario.views.facebook_authorize'),
    
    # Links produtos
    (r'^dialog_add_oferta/$', 'kopenDjango.produto.views.dialog_add_oferta'),
    (r'^dialog_report_oferta/$', 'kopenDjango.produto.views.dialog_report_oferta'),
    (r'^ajax_produtos/$', 'kopenDjango.produto.views.ajax_produtos'),
    (r'^ajax_locais/$', 'kopenDjango.produto.views.ajax_locais'),
    (r'^ajax_check_local/$', 'kopenDjango.produto.views.ajax_check_local'),
    (r'^ajax_check_produto/$', 'kopenDjango.produto.views.ajax_check_produto'),
    (r'^ajax_oferta/$', 'kopenDjango.produto.views.ajax_oferta'),    
    (r'^busca/$', 'kopenDjango.produto.views.busca'),
    (r'^oferta/$', 'kopenDjango.produto.views.oferta'),
    (r'^oferta_shared/$', 'kopenDjango.produto.views.oferta_shared'),
    (r'^oferta_commented/$', 'kopenDjango.produto.views.oferta_commented'),        
    (r'^busca_shared/$', 'kopenDjango.produto.views.busca_shared'),
    (r'^oferta_like/$', 'kopenDjango.produto.views.oferta_like'),
    (r'^oferta_dislike/$', 'kopenDjango.produto.views.oferta_dislike'),
    (r'^oferta_notify/$', 'kopenDjango.produto.views.oferta_notify'),
    (r'^add_oferta/$', 'kopenDjango.produto.views.add_oferta'),
    (r'^report_oferta/$', 'kopenDjango.produto.views.report_oferta'),
    (r'^local_searched/$', 'kopenDjango.produto.views.local_searched'),
)
