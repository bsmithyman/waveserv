from django.template import RequestContext
from django.template.defaultfilters import escape
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse
from django.views.decorators.gzip import gzip_page
from server.models import RenderResult
import os
import glob
import datetime

try:
  from server.handlers import redict, redict_meta, redict_auth, handle
except Exception as errorresult:
  print ('Unable to import file handlers from waveserv.server.handlers!\n%s'%errorresult)
  raise

from server.models import Project
project = Project.objects.all()[0]
print project

page_titles = {	'index':	'Index',
		'show':		'Figure: %s',
}

defSortKey = 'filename'
freshthresh = 0.1

DEBUG = project.debug
VERBOSE = project.verbose
DIBUPATH = project.dibupath
try:
  os.mkdir(DIBUPATH)
except OSError as (errno, strerror):
  if (errno != 17): # Exists
    raise

# ------------------------------------------------------------------------
# Helper functions

def clean_input (filename):
  result = os.path.basename(filename)
  return result

# ========================================================================
# View Handlers
#
# NB: The following are handled by Django in urls.py
# /download/*
# /media/*

# ------------------------------------------------------------------------
# Main site index

@gzip_page
def view_index (request):
  s = request.session
  r = request.REQUEST
  if ('SortKey' in r):
    s['SortKey'] = r['SortKey']
    return redirect('index')
  elif ('SortKey' in s):
    sortby = s['SortKey']
  else:
    sortby = defSortKey
  
  q = QueryDict('pagetitle=%s'%page_titles['index'])
  q = q.copy()

  cwd = os.getcwd()
  listing = glob.glob('*')

  matchlist = []

  youngest = 0
  oldest = int(datetime.datetime.now().strftime('%s'))
  for key, value in redict_auth.iteritems():
    matchobj = [result for result in [value[2].match(item) for item in listing] if result]
    matches = [part.group() for part in matchobj]
    extras = [part.groupdict() for part in matchobj]
    modified = [datetime.datetime.fromtimestamp(os.path.getmtime(item)) for item in matches]
    size = [os.path.getsize(item) for item in matches]
    freq = [result['freq'] if ('freq' in result and result['freq'] != '') else None for result in extras]
    iteration = [int(result['iter']) if ('iter' in result and result['iter'] != '') else None for result in extras]


    for item in modified:
      ts = int(item.strftime('%s'))
      if (youngest < ts):
        youngest = ts
      if (oldest > ts):
        oldest = ts

    stamprange = youngest - oldest

    freshnesses = [(float(mtime.strftime('%s'))-oldest) / stamprange for mtime in modified]
    freshnesses = [fresh if (fresh > freshthresh) else None for fresh in freshnesses]

    items = []
    for i in xrange(len(matches)):
      items.append({
		'filename':	matches[i],
		'modified':	modified[i],
		'size':		size[i],
		'iteration':	iteration[i],
		'frequency':	freq[i],
		'freshness':	freshnesses[i],
      })
    matchkeys = {
		'name':		key,
		'id':		value[0],
		'description':	value[1],
		'result':	items
    }
    matchlist.append(matchkeys)

  q.update({	'cwd': 		cwd,
		'listing':	listing,
		'matchlist':	matchlist,
		'sortby':	sortby,
		'sortkeys':	[
				'filename',
				'iteration',
				'frequency',
				'size',
				'modified',
		],
  })

  return render_to_response('index.html', q, context_instance=RequestContext(request))

# ------------------------------------------------------------------------
# View renderer

def view_show (request, renderpath):
  q = QueryDict('pagetitle=%s'%(page_titles['show']%renderpath))
  q = q.copy()

  q['renderpath'] = reverse('render', args=[renderpath])
  q['downloadpath'] = reverse('download', args=[renderpath])

  return render_to_response('show.html', q, context_instance=RequestContext(request))

# ------------------------------------------------------------------------
# File PNG renderer

# Can enable gzip compression, but it doesn't do much for PNG files
# @gzip_page
def view_render (request, filename):
  filedt = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
  dirty = True
  try:
    rr = RenderResult.objects.get(filename=filename)
    if (rr.lastmodified == filedt):
      dirty = False
  except:
    rr = RenderResult(filename=filename, lastmodified=filedt, requesthash='',diskbuffer='%s/%s.png'%(DIBUPATH, filename))
    rr.save()

  if (dirty):
    if (VERBOSE): print('DIRTY: Rendering %s...'%filename)
    image = handle(clean_input(filename))
    if (image != None):
      image.save(rr.diskbuffer, 'PNG')
      response = HttpResponse(mimetype='image/png')
      image.save(response, 'PNG')
      return response
    else:
      raise Http404
  else:
    if (VERBOSE): print('CLEAN: Reading %s from cache...'%filename)
    fp = open(rr.diskbuffer, 'rb')
    response = HttpResponse(fp, mimetype='image/png')
    return response

