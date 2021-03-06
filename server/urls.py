from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
import server.settings as settings
import os.path

CWD = os.getcwd()

# Set up automatic traversal of source tree to find the static file dir
SCRIPTDIR = os.path.abspath(os.path.dirname(globals()['__file__'])+'/..')
STATICDIR =  SCRIPTDIR + '/media'

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATICDIR}),
    url(r'^$', RedirectView.as_view(url='/index')),
    url(r'^index$', 'server.views.view_index', name='index'),
    url(r'^render/(?P<filename>.*).png$', 'server.views.view_render', name='render'),
    url(r'^show/(?P<renderpath>.*)$', 'server.views.view_show', name='show'),
    url(r'^download/(?P<path>.*)$', 'django.views.static.serve', {'document_root': CWD}, name='download'),
    url(r'^plugins/', include('plugins.urls', app_name='plugins')),
)
