#-*- coding: utf-8 -*-
"""
kopenDjango Social network to share sales promotions
https://github.com/jfmedeirosneto/kopendjango
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import DateTimeInput
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

# MyAdminSplitDateTime
# Necessario pois foi customizado widgets com date_format e time_format
# customizado tambem decompress pois gerava erro
class MyAdminSplitDateTime(forms.MultiWidget):
    date_format = settings.DATE_INPUT_FORMATS[0]
    time_format = settings.TIME_INPUT_FORMATS[0]
        
    def __init__(self, attrs=None, date_format=None, time_format=None):
        if date_format:
            self.date_format = date_format
        if time_format:
            self.time_format = time_format
        widgets = (AdminDateWidget(attrs=attrs, format=self.date_format),
                   AdminTimeWidget(attrs=attrs, format=self.time_format))
        super(MyAdminSplitDateTime, self).__init__(widgets, attrs)        

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="datetime">%s %s<br />%s %s</p>' % \
            (_('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))
        
    def decompress(self, value):
        if value:
            if isinstance(value, datetime):
                return [value.date(), value.time().replace(microsecond=0)]
            else:
                #Elimina microseconds
                date_object = datetime.strptime(value.split('.')[0], DateTimeInput.format)
                return [date_object.date(), date_object.time().replace(microsecond=0)]
        return [None, None]

# MyAdminImageWidget
class MyAdminImageWidget(forms.FileInput):
    def __init__(self, attrs={}):
        super(MyAdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = ''
        if value and hasattr(value, "url"):
            output += '\n<table>'
            output += '\n<tbody>'
            output += '\n<tr class="None">'
            output += '\n<td rowspan="2"><img src="%s" style="height: 56px; padding-right: 5px;" /></a></td>' % (value.url)
            output += '\n<td><a target="_blank" href="%s" id="image-a" onclick="return showPopup(this);">%s</a></td>' % (value.url, value.url)
            output += '\n</tr>'
            output += '\n<tr class="None">'
            output += '\n<td>%s</td>' % (super(MyAdminImageWidget, self).render(name, value, attrs))
            output += '\n</tr>'
            output += '\n</tbody>'
            output += '\n</table>'
        else:
            output +=  super(MyAdminImageWidget, self).render(name, value, attrs)
        return mark_safe(u''.join(output))