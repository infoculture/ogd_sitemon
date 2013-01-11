#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import sys
import random
import os
import os.path
import time
import optparse
import datetime
import socket
import traceback
import re
import time

import signal, xml, urllib
from xml.dom.ext.reader import HtmlLib, Sgmlop, PyExpat
import xml.xpath
from urlgrabber import urlopen
import re
import hashlib, zlib, binascii

import pycurl, StringIO


def calc_avg(values):
    s = 0
    for v in values:
        s += v
    return s / len(values) if len(values) > 0 else 0

def mark_periods(page):
    from smon import models        
    models.Period.objects.filter(page=page).delete()
    probes = models.ProbeValue.objects.filter(page=page).order_by('probe_date')
    start_probe = None
    values = []
    last_probe = None
    for v in probes:
        if start_probe is None:
            start_probe = v
            values.append(v.resp_time)
        elif v.http_status != start_probe.http_status:
            ddiff = v.probe_date - start_probe.probe_date
            per_len = ddiff.seconds + ddiff.days *86400
            per = models.Period(start_probe=start_probe, end_probe=v, per_len=per_len, page=page, http_status=start_probe.http_status, resp_time=calc_avg(values))
            per.save()
            start_probe = v
            values.append(v.resp_time)
        else:
            values.append(v.resp_time)
        last_probe = v        
    if last_probe.http_status == start_probe.http_status:
        ddiff = last_probe.probe_date - start_probe.probe_date
        per_len = ddiff.seconds + ddiff.days *86400
        per = models.Period(start_probe=start_probe, end_probe=last_probe, per_len=per_len, page=page, http_status=start_probe.http_status, resp_time=calc_avg(values))
        per.save()        
        

def mark_days(page):
    from smon import models            
    today = datetime.date.today()
    week = [today,]
    for n in range(1, 7, 1):
        week.append(today - datetime.timedelta(days=n))
    for day in week:
        probes = models.ProbeValue.objects.filter(page=page, probe_date__year=day.year, probe_date__month=day.month, probe_date__day=day.day)
        if len(probes) > 0:
            all_time = 0
            unavail_time = 0
            resp_time = 0
            last_good = True
            for probe in probes:
                if probe.http_status in [200, 301]:
                    last_good = True
                else:
                    unavail_time += 600
                resp_time += probe.resp_time
                all_time += 600
            resp_time = resp_time / len(probes)
            day, created = models.DayStat.objects.get_or_create(page=page,theday=day)
            day.probe_time = all_time
            day.unavail_time = unavail_time
            day.unavail_percent = (unavail_time * 100.0) / 86400
            day.avail_time = all_time - unavail_time
            day.resp_time = resp_time
            day.save()
            print day, len(probes), all_time, day.avail_time, unavail_time, day.unavail_percent, resp_time
    return
        
        
def mark_all_periods():
    from smon import models        
    for page in models.WatchedPage.objects.all():
        mark_periods(page)


def mark_all_days():
    from smon import models        
    for page in models.WatchedPage.objects.all():
        mark_days(page)

def clean_all():
    from smon import models        
    models.Event.objects.all().delete()
    

def main():
    """ Main function. Nothing to see here. Move along.
    """
    parser = optparse.OptionParser(usage='%prog [options]', version="0.0.1")
    parser.add_option('--settings', \
      help='Python path to settings module. If this isn\'t provided, the DJANGO_SETTINGS_MODULE enviroment variable will be used.')

    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', \
      default=False, help='Verbose output.')
    options = parser.parse_args()[0]
    if options.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = options.settings
    else:
        os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
#    clean_all()
    mark_all_periods()
    mark_all_days()

    
if __name__ == '__main__':
    main()



