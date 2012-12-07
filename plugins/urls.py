from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import *

listing = [
	{	'urltag': 'plugins.meta.view_meta',
		'shortname': 'Meta',
		'longname': 'Meta-information Report'}
]

urlpatterns = patterns('',
  url(r'^$', redirect_to, {'url': '/plugins/index'}),
  url(r'^index$', direct_to_template, {'template': 'plugins.html'}),
  url(r'^meta$', 'plugins.meta.view_meta', name='meta'),
  url(r'^meta/(?P<path>.*)$', 'plugins.meta.view_metarender', name='metarender'),
)
