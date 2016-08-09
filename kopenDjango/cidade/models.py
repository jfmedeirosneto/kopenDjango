#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.db import models

class Cidade(models.Model):
    nome = models.CharField('Nome',
                            max_length=128,
                            help_text=u'Nome da cidade.')
    active = models.BooleanField('Ativo',
                                 default=True,
                                 help_text=u'Cidade ativa.')        
    
    def __unicode__(self):
        return self.nome    
    
    class Meta:
        verbose_name = u'Cidade'
        verbose_name_plural = u'Cidades'
        ordering = ['nome']