from django.conf.urls.defaults import *
from django.views.generic.simple import *

urlpatterns = patterns('',
  (r'^$', redirect_to, {'url': '/plugins/index'}),
  (r'^index$', direct_to_template, {'template': 'plugins.html'})
)
