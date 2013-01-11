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



def probe_page(page):
    m = hashlib.md5()
    from smon import models
    print 'Probing', page.url.encode('utf8', 'replace')    
    b = StringIO.StringIO()
    start_time = datetime.datetime.now()
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, page.url.encode('utf8'))
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 3)
        c.setopt(pycurl.TIMEOUT, 15)
        c.perform()
        http_status = int(c.getinfo(pycurl.HTTP_CODE))    
    except pycurl.error:
        http_status = 900
        pass
    end_time = datetime.datetime.now()
    elapsed = end_time - start_time    
    print elapsed
    data = b.getvalue()
    prev = models.ProbeValue.objects.filter(page=page).order_by('-probe_date')[0:1]
    if len(prev) > 0:
        prev = prev[0]
    else:
        prev = None
    result = models.ProbeValue()
    result.page = page
    result.probe_date = datetime.datetime.now()
    result.http_status = http_status
    result.status = models.PAGE_STATUS_OK if result.http_status in [200, 301] else models.PAGE_STATUS_ERROR
    m.update(data)
    result.phash = m.hexdigest()
    result.page_len = len(data)
    result.resp_time = elapsed.microseconds + elapsed.seconds*1000000
    result.save()    
    if prev is not None:
        if result.page_len == prev.page_len and result.phash == prev.phash:
            result.is_page_changed = False
        else:
            result.is_page_changed = True
        if prev.http_status != result.http_status:
            if result.http_status in [200, 301] and prev.http_status not in [200, 301]:
                event = models.Event(page=page, event_date=datetime.datetime.now(), title=u'Страница: %s стала доступна' %(page.name), eventtype=models.EVENT_TYPE_PAGEAVAILABLE, text=u'Страница %s теперь доступна.\n Время отклика страницы %d микросекунд.\n Размер страницы %d байт.\n HTTP код %d.' %(page.name, result.resp_time, result.page_len, result.http_status))
                event.save()
            elif prev.http_status in [200, 301] and result.http_status not in [200, 301]:
                event = models.Event(page=page, event_date=datetime.datetime.now(), title=u'Страница: %s стала недоступна' %(page.name), eventtype=models.EVENT_TYPE_PAGEUNAVAILABLE, text=u'Страница %s недоступна.\n Время отклика страницы %d микросекунд.\n Размер страницы %d байт.\n HTTP код %d.' %(page.name, result.resp_time, result.page_len, result.http_status))
                event.save()
    print 'End probing', result.http_status, result.resp_time
    

def probe_all():
    from smon import models        
    for page in models.WatchedPage.objects.all():
        probe_page(page)

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

    probe_all()

    
if __name__ == '__main__':
    main()



