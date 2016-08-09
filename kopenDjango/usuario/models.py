#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from django.db import models

from kopenDjango.base.utils import timenow

class Usuario(models.Model):
    user = models.CharField('Usuário',
                            max_length=32,
                            help_text=u'Nome de usuário.')
    name = models.CharField('Nome completo',
                            max_length=200,
                            help_text=u'Nome completo.')    
    email = models.EmailField('E-mail',
                            max_length=200,
                            help_text=u'Endereço de e-mail.')    
    password = models.CharField('Senha',
                            max_length=32,
                            help_text=u'Senha para acesso.')
    facebook_id = models.BigIntegerField('Facebook Id',
                                         default=0,
                                         help_text=u'Facebook Id.')
    active = models.BooleanField('Ativo',
                                 default=True,
                                 help_text=u'Usuário ativo.')
    points = models.IntegerField('Pontuação',
                                 default=50,
                                 help_text=u'Pontuação do usuário.')    
    failures = models.IntegerField('Falhas de login',
                                   default=0,
                                   help_text=u'Falhas de logins.')    
    created = models.DateTimeField('Criado',
                                   default=timenow)
    modified = models.DateTimeField('Modificado',
                                    default=timenow)
    password_hash = models.CharField('Hash',
                            null=True,
                            max_length=512,
                            help_text=u'Password Hash.')    

    def save(self, *args, **kwargs):
        self.modified = timenow()
        super(Usuario, self).save(*args, **kwargs)
                
    def __unicode__(self):
        return self.user    
    
    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'
        ordering = ['user']        
    
