# -*- coding: utf8 -*-
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from smon.models import *

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'description', 'date_created')
    search_fields = ['name', 'url', 'description']
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('website','name', 'url', 'description',)
    search_fields = ['name', 'url', 'description']
    list_filter = ['website', ]

class EventAdmin(admin.ModelAdmin):
    list_display = ('page', 'event_date', 'title', 'text', 'eventtype')
    ordering = ('-event_date',)
    list_filter = ['eventtype', 'page']
    search_fields = ['title', 'text']

class ProbeValueAdmin(admin.ModelAdmin):
    list_display = ('page', 'probe_date', 'status', 'http_status', 'resp_time', 'page_len', 'phash', 'is_page_changed')
    ordering = ('-probe_date',)
    list_filter = ['page','http_status', 'status', 'is_page_changed']


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('page', 'per_len', 'http_status', 'start_probe', 'end_probe', 'resp_time')
    ordering = ('-start_probe',)
    list_filter = ['page',]

class DayStatAdmin(admin.ModelAdmin):
    list_display = ('page', 'theday', 'unavail_time', 'unavail_percent', 'avail_time', 'resp_time')
    ordering = ('-theday',)
    list_filter = ['page',]



    
admin.site.register(Website, WebsiteAdmin)
admin.site.register(WatchedPage, PageAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(DayStat, DayStatAdmin)
admin.site.register(ProbeValue, ProbeValueAdmin)
