from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView, TemplateView

listing = [
	{	'urltag': 'plugins.geom.view_geom',
		'shortname': 'Geom.',
		'longname': 'Acquision and Model Geometry'},

	{	'urltag': 'plugins.psf.view_psf',
		'shortname': 'PSF',
		'longname': '2.5D PSF Analysis'},

	{	'urltag': 'plugins.cycleskip.view_cycleskip',
		'shortname': 'CycleSkip',
		'longname': 'Cycle Skip Analysis'},
]

urlpatterns = patterns('',
  url(r'^$', RedirectView.as_view(url='/plugins/index')),
  url(r'^index$', TemplateView.as_view(template_name='plugins.html')),

  url(r'^geom$', 'plugins.geom.view_geom', name='geom'),
  url(r'^geom/(?P<path>.*)$', 'plugins.geom.view_geomrender', name='geomrender'),

  url(r'^psf$', 'plugins.psf.view_psf', name='psf'),
  url(r'^psf/(?P<path>.*)$', 'plugins.psf.view_psfrender', name='psfrender'),

  url(r'^cycleskip$', 'plugins.cycleskip.view_cycleskip', name='cycleskip'),
  url(r'^cycleskip/(?P<path>.*)$', 'plugins.cycleskip.view_cycleskiprender', name='cycleskiprender'),
)
