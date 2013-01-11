# -*- coding: utf-8 -*-

"""
Site monitoring
Ivan Begtin
urls.py
"""

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to, direct_to_template
from django.utils.translation import gettext_lazy as _


from smon import views

urlpatterns = patterns('',
    url(r'^$', views.home_view),
    (r'^indicators/(?P<obj_id>\d+)/$', views.indicator_view),
    (r'^indicators/(?P<obj_id>\d+)/events/feed/$', views.events_feed_view),
    url(r'^indicators/$', views.indicators_list_view),
    url(r'^about/$', direct_to_template, {'template' : 'about.html'}),
    url(r'^export/probes/1m/$', views.export1m_view),
    url(r'^export/probes/7d/$', views.export7d_view),
    url(r'^export/probes/24h/$', views.export24h_view),
    url(r'^export/probes/$', views.export_probes_view),
    url(r'^export/periods/$', views.export_periods_view),
    url(r'^export/days/$', views.export_days_view),
    url(r'^export/events/$', views.events_feed_view),
    )
