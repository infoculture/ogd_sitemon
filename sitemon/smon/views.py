# -*- coding:utf8 -*-
"""
Site monitor
Ivan Begtin
views.py
"""

from django.utils import feedgenerator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.template import Context, loader, RequestContext
from django.views.generic.list_detail import object_list, object_detail
from django.core import serializers
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from StringIO import StringIO

from django.utils.xmlutils import SimplerXMLGenerator
from django.conf import settings
from django.core.cache import cache

from smon import models
import sys, csv

import traceback, datetime
import urlparse
import simplejson

def indicators_list_view(request):
    """Просмотр списка источников данных"""
    params = {}
    objects = models.WatchedPage.objects.filter(website__slug='zakupkigovru').order_by('name')
    params['object_list'] = objects
    return render_to_response('indicators.html', params)

def indicator_view(request, obj_id):
    """Просмотр источника данных"""
    queryset = models.WatchedPage.objects.filter(website__slug='zakupkigovru').order_by('name')
    params = {'base_url' : '/indicators/', 'total' : len(queryset)}
    return object_detail(request, queryset, object_id=obj_id, template_name='ind.html', extra_context=params)


def home_view(request):
    params = {}
    params['indicators'] = models.WatchedPage.objects.filter(website__slug='zakupkigovru').order_by('name')
    params['object'] = models.WatchedPage.objects.get(slug='zakallzak')
    return render_to_response('home.html', params)
#    return render_to_response('catalog.html', params)


def format_date(d):
    return '%d-%d-%d %d:%d:%d' %(d.year, d.month, d.day, d.hour, d.minute, d.second)

EXPORT_PROBE_KEYS = ['site_slug', 'site_name', 'ind_id', 'ind_name', 'probe_date', 'resp_time', 'http_status']

def __get_probe_row(r):
    row = [r.page.website.slug, r.page.website.name.encode('utf8', 'ignore'), r.page.id, r.page.name.encode('utf8', 'ignore'), format_date(r.probe_date), str(r.resp_time), str(r.http_status)]
    return row

def export_probes_view(request, key=None):
    ind_id = request.GET.get('ind', None)
    now = datetime.datetime.now()
    if key == '1m':       
        delta = datetime.timedelta(days=30)
    elif key == '7d':
        delta = datetime.timedelta(days=7)
    elif key == '24h':
        delta = datetime.timedelta(hours=24)
    else:
        key = '7d'
        delta = datetime.timedelta(days=7)
    last = now - delta
    if ind_id is not None and ind_id.isdigit():    
        data = models.ProbeValue.objects.filter(probe_date__gt=last, page__id=int(ind_id)).order_by('-probe_date')
        filename = 'probes_%s_ind_%s.csv' %(key, ind_id)
    else:
        filename = 'probes_%s.csv' %(key,)
        data = models.ProbeValue.objects.filter(probe_date__gt=last, page__website__slug='zakupkigovru').order_by('-probe_date')
    io = StringIO()
    wr = csv.writer(io, dialect='excel')
    wr.writerow(EXPORT_PROBE_KEYS)
    for r in data:
        wr.writerow(__get_probe_row(r))
        value = io.getvalue()
    resp = HttpResponse(value, mimetype="text/csv")
    resp['Content-Disposition'] = 'attachment; filename=%s' %(filename)
    return resp


def export24h_view(request):
    return export_probes_view(request, key='24h')

def export7d_view(request):
    return export_probes_view(request, key='7d')

def export1m_view(request):
    return export_probes_view(request, key='1m')


def events_feed_view(request):
    """Просмотр RSS событий"""
    from django.utils import feedgenerator
    ind = request.GET.get('ind', None)
    f = feedgenerator.Atom1Feed(title=u'Монитор сайтов, лента событий.', language=u"ru", link=u"http://sitemon.opengovdata.ru/", description=u'Событий в процессе мониторинга')
    if ind is not None:
        objects = models.Event.objects.filter(page__id=ind).order_by('-event_date')[0:20]    
    else:
        objects = models.Event.objects.all().order_by('-event_date')[0:20]    
    for p in objects:
        f.add_item(title=p.title, link="http://sitemon.opengovdata.ru/events/%s/" %(str(p.id)), description=p.text, pubdate=p.event_date)
    return HttpResponse(f.writeString('utf8'), mimetype='text/xml;')

EXPORT_PERIOD_KEYS = ['site_slug', 'site_name', 'ind_id', 'ind_name', 'start_date', 'per_length', 'resp_time', 'http_status']

def __get_period_row(r):
    row = [r.page.website.slug, r.page.website.name.encode('utf8', 'ignore'), r.page.id, r.page.name.encode('utf8', 'ignore'), format_date(r.start_probe.probe_date), str(r.per_len), str(r.resp_time), str(r.http_status)]
    return row

def export_periods_view(request, key=None):
    ind_id = request.GET.get('ind', None)
    if ind_id is not None and ind_id.isdigit():    
        filename = 'periods_ind_%s.csv' %(ind_id)
        data = models.Period.objects.filter(page__id=int(ind_id)).order_by('-id')
    else:
        filename = 'periods.csv'
        data = models.Period.objects.filter(page__website__slug="zakupkigovru").order_by('-id')
    io = StringIO()
    wr = csv.writer(io, dialect='excel')
    wr.writerow(EXPORT_PERIOD_KEYS)
    for r in data:
        wr.writerow(__get_period_row(r))
        value = io.getvalue()
    resp = HttpResponse(value, mimetype="text/csv")
    resp['Content-Disposition'] = 'attachment; filename=%s' %(filename)
    return resp

EXPORT_DAY_KEYS = ['site_slug', 'site_name', 'ind_id', 'ind_name', 'day', 'unavail_time', 'unavail_percent', 'resp_time', ]


def format_thedate(d):
    return "%d.%d.%d" %(d.day, d.month, d.year)

def __get_day_row(r):
    row = [r.page.website.slug, r.page.website.name.encode('utf8', 'ignore'), r.page.id, r.page.name.encode('utf8', 'ignore'), format_thedate(r.theday), str(r.unavail_time), str(r.unavail_percent), str(r.resp_time)]
    return row

def export_days_view(request, key=None):
    ind_id = request.GET.get('ind', None)
    if ind_id is not None and ind_id.isdigit():    
        filename = 'days_ind_%s.csv' %(ind_id)
        data = models.DayStat.objects.filter(page__id=int(ind_id)).order_by('theday')
    else:
        filename = 'days.csv'
        data = models.DayStat.objects.filter(page__website__slug="zakupkigovru").order_by('theday')
    io = StringIO()
    wr = csv.writer(io, dialect='excel')
    wr.writerow(EXPORT_DAY_KEYS)
    for r in data:
        wr.writerow(__get_day_row(r))
        value = io.getvalue()        
    resp = HttpResponse(value, mimetype="text/csv")
    resp['Content-Disposition'] = 'attachment; filename=%s' %(filename)
    return resp
