from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'', include('smon.urls')),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/var/www/sitemon.opengovdata.ru/html/css'}),    
    (r'^gfx/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/var/www/sitemon.opengovdata.ru/html/gfx'}),    
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/var/www/sitemon.opengovdata.ru/html/js'}),    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/var/www/sitemon.opengovdata.ru/html/media'}),    
)
