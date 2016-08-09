#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import locale, re

from django import template
register = template.Library()

from kopenDjango.base.utils import remove_accents

def group(n, sep = ','):
    s = str(abs(n))[::-1]
    groups = []
    i = 0
    while i < len(s):
        groups.append(s[i:i+3])
        i+=3
    retval = sep.join(groups)[::-1]
    if n < 0:
        return '-%s' % retval
    else:
        return retval

def format_currency(value):
    #Aceita valores monetarios com 3 e 2 digitos :)
    c = locale.localeconv()["currency_symbol"]
    v = locale.format("%.3f", value, grouping=False)
    vg = group(int(v[:-4]),'.')
    vd = v[-4:] 
    v = vg + vd
    #Verifica ultimo caracter zerado
    if v[-1:] == "0":
        #Exclui ultimo caracter
        v = v[:-1]
    return  c + v
format_currency.is_safe = True

def previus_id(l,i):
    return l[i-1].id
previus_id.is_safe = True

def next_id(l,i):
    return l[i+1].id
next_id.is_safe = True

def callMethod(obj, methodName):
    method = getattr(obj, methodName)
    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
    obj.__callArg += [arg]
    return obj

def urlify(s):
    s = s.lower()
    s = remove_accents(s)
    s = re.sub("[^\w\s]", "", s)
    s = re.sub("\s+", "+", s)
    return s
 
register.filter("call", callMethod)
register.filter("args", args)
register.filter("format_currency", format_currency)
register.filter("previus_id", previus_id)
register.filter("next_id", next_id)
register.filter("urlify", urlify)

def mul(value, arg):
    "Multiplies the arg and the value"
    return int(value)*int(arg)

def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value)-int(arg)

def div(value, arg):
    "Divides the value by the arg"
    return int(value)/int(arg)

def tagmin(value, arg):
    return min(int(value), int(arg))

def tagmax(value, arg):
    return max(int(value), int(arg))

register.filter('mul', mul)
register.filter('sub', sub)
register.filter('div', div)
register.filter('min', tagmin)
register.filter('max', tagmax)