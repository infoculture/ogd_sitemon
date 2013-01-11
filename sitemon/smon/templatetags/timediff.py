# -*- coding: utf-8 -*-
from django import template
import locale
locale.setlocale(locale.LC_ALL, 'russian')
register = template.Library()
 
 
@register.filter()
def timediff(value):
    return '.'.join(map(str, [value / 1000000, value % 1000000]))
