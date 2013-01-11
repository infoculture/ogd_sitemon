# -*- coding: utf-8 -*-
from django import template
import locale
locale.setlocale(locale.LC_ALL, 'russian')
register = template.Library()
 
 
@register.filter()
def datediff(value):
    parts = []
    hours = value / 3600
    if hours == 1:
        parts.append(u'1 час')
    elif hours in [2, 3, 4]:
        parts.append(u'%d часа' %(hours))
    else:
        parts.append(u'%d часов' %(hours))
    minutes = (value / 60) - (hours * 60)
    if minutes % 10 == 1:
        parts.append(u'%d минута' %(minutes))
    elif minutes % 10 in [2, 3, 4]:
        parts.append(u'%d минуты' %(minutes))
    else:
        parts.append(u'%d минут' %(minutes))
    seconds = value % 60
    if seconds % 10 == 1:
        parts.append(u'%d секунда' %(seconds))
    elif minutes % 10 in [2, 3, 4]:
        parts.append(u'%d секунды' %(seconds))
    else:
        parts.append(u'%d секунд' %(seconds))    
    return u' '.join(parts)
