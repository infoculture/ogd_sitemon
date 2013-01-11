#-*- coding: utf-8 -*-
"""
Site monitoring models

by Ivan Begtin (c) 2011
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

PAGE_STATUS_OK = 10
PAGE_STATUS_ERROR = 20

PAGE_STATUSES = [
    (PAGE_STATUS_OK, u'Ok',),
    (PAGE_STATUS_ERROR, u'Error',),
]

EVENT_TYPE_PAGEUNAVAILABLE = 10
EVENT_TYPE_PAGESLOWDOWN = 20
EVENT_TYPE_PAGEAVAILABLE = 30
EVENT_TYPE_VERYCHANGED = 40

EVENT_TYPES = [
    (EVENT_TYPE_PAGEUNAVAILABLE, u'Page unavailable'),
    (EVENT_TYPE_PAGESLOWDOWN, u'Page slowed down'),
    (EVENT_TYPE_PAGEAVAILABLE, u'Page available'),
    (EVENT_TYPE_VERYCHANGED, u'Page contents changed too much')
]


class Website(models.Model):
    """Модель веб-сайта"""
    slug = models.CharField(name=_('slug'), max_length=50, unique=True)
    name = models.CharField(name=_('name'), max_length=200)
    url = models.CharField(name=_('url'), max_length=500)
    description = models.TextField(name=_('description'))
    date_created = models.DateTimeField(name=u'Дата создания', auto_now_add=True)
    
    def __unicode__(self):
        return u'%s' %(self.name)

    class Meta:
        verbose_name = u'Веб сайт'
        verbose_name_plural = u'Веб сайты'


class WatchedPage(models.Model):
    """Модель страницы для наблюдения"""
    slug = models.CharField(name=_('slug'), max_length=50, unique=True)
    website = models.ForeignKey(Website)
    name = models.CharField(name=_(u'name'), max_length=200)
    url = models.CharField(name=_(u'url'), null=True, blank=True, max_length=500)
    description = models.TextField(name=_('description'), blank=True, null=True)
    always_keep_page = models.BooleanField(name=_('always keep page'), default=False)
    keep_error_page = models.BooleanField(name=_('keep error page'), default=False)    
    date_created = models.DateTimeField(name=u'Дата создания', auto_now_add=True)
                    
    class Meta:
        verbose_name = u'Веб-страница'
        verbose_name_plural = u'Веб-страницы'
        
    def getvalues(self):
        return ProbeValue.objects.filter(page=self).order_by('-probe_date')[0:200]

    def getperiods(self):
        return Period.objects.filter(page=self).order_by('-id')[0:200]

    def getevents(self, limit=3):
        return Event.objects.filter(page=self).order_by('-id')[0:limit]

    def getdays(self, limit=15):
        today = datetime.date.today()
        day = today - datetime.timedelta(days=7)
        return DayStat.objects.filter(page=self, theday__gt=day).order_by('theday')
        
    def watch_time(self):
        wt = 0
        all = Period.objects.filter(page=self).order_by('-id')[0:200]
        for p in all:
            wt += p.per_len
        return wt

    def inactive_time(self):        
        wt = 0
        all = Period.objects.filter(page=self).exclude(http_status=200).order_by('-id')[0:200]
        for p in all:
            wt += p.per_len
        return wt
        
    def __unicode__(self):
        return self.website.slug + ': ' + self.name

class ProbeValue(models.Model):
    """Результат проверки сайта"""
    page = models.ForeignKey(WatchedPage)
    probe_date = models.DateTimeField(name=_('probe date'), db_index=True)
    resp_time = models.IntegerField(name=_('response time'), default=0)
    http_status = models.IntegerField(name=_('http status'), default=0)
    page_len = models.IntegerField(name=_('page length'), default=0)
    phash = models.CharField(name=_('hash'), max_length=50, blank=True, null=True)
    status = models.IntegerField(name=_('status'), choices=PAGE_STATUSES, default=PAGE_STATUS_ERROR)
    is_page_changed = models.BooleanField(name=_('is page changed'), default=False)
    
                    
    class Meta:
        verbose_name = u'Значение показателя'
        verbose_name_plural = u'Значения показателей'
        
    def __unicode__(self):
        return self.page.name + ', probe: ' + str(self.probe_date)

class Period(models.Model):
    """Период работы сайта"""
    page = models.ForeignKey(WatchedPage)
    start_probe = models.ForeignKey(ProbeValue, related_name="start_probe")
    end_probe = models.ForeignKey(ProbeValue, null=True, blank=True, related_name="end_probe")
    per_len = models.IntegerField(name=_('period length (seconds)'), default=0)
    http_status = models.IntegerField(name=_('http status'), default=0)
    resp_time = models.IntegerField(name=_('response time'), default=0)

    class Meta:
        verbose_name = u'Период'
        verbose_name_plural = u'Периоды'
        
    def __unicode__(self):
        return self.page.name + u', period: ' + unicode(self.start_probe.probe_date) + ", length: " + str(self.per_len)

class DayStat(models.Model):
    """Daily statistics"""
    page = models.ForeignKey(WatchedPage)
    theday = models.DateField(name=_('day'), db_index=True)
    probe_time = models.IntegerField(name=_('probe time'), default=0)
    unavail_time = models.IntegerField(name=_('probe unavail'), default=0)
    unavail_percent = models.FloatField(name=_('probe unavail percent'), default=0.0)
    avail_time = models.IntegerField(name=_('probe avail'), default=0)
    resp_time = models.IntegerField(name=_('response time'), default=0)
    
    class Meta:
        verbose_name = u'День'
        verbose_name_plural = u"Дни"
    
    def __unicode__(self):
        return unicode(self.theday)
       

class Event(models.Model):
    """Event"""
    page = models.ForeignKey(WatchedPage)
    event_date = models.DateTimeField(name=_('event date'), db_index=True)
    title = models.CharField(name=_('title'), max_length=300)
    text = models.TextField(name=_('text'))
    eventtype = models.IntegerField(name=_('event type'), choices=EVENT_TYPES)
    
    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'
        
    def __unicode__(self):
        return str(self.event_date) + ": " + self.title
        
        