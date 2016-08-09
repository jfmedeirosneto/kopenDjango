#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.contrib import admin

from kopenDjango.cidade.models import Cidade

class CidadeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Cidade, CidadeAdmin);