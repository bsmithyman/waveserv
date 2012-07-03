import os
import glob
import datetime

# Imports for Django functionality
from django.template import RequestContext
from django.template.defaultfilters import escape
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse
from django.views.decorators.gzip import gzip_page

# Data model used to cache rendered images
from server.models import RenderResult

# Project information from pygeo
from pygeo.fullpy import readini

# Imports the handler function that renders plots, as well as dictionaries
# of compiled regular-expression objects that are used to interrogate the
# listing of files in the CWD.
try:
  from server.handlers import redict, redict_meta, redict_auth, handle
except Exception as errorresult:
  print ('Unable to import file handlers from waveserv.server.handlers!\n%s'%errorresult)
  raise

try:
  import server.helper as helper
except Exception as errorresult:
  print('Unable to import helper functions from waveserv.server.helper!\n%s'%errorresult)
  raise

# Contains information from the "waveserv" wrapper script, including parameters
# that are read from the projnm.ini file.
from server.models import Project
project = Project.objects.all()[0]
print project

# Dictionary that controls the page titles
page_titles = {	'index':	'Index',
		'show':		'Figure: %s',
		'meta':		'Meta Information',
}

# Defaults
defSortKey = 'filename'
freshthresh = 0.1

DEBUG = project.debug
VERBOSE = project.verbose
DIBUPATH = project.dibupath
PROJNM = project.projnm

# Attempts to create the directory for caching of images
try:
  os.mkdir(DIBUPATH)
except OSError as (errno, strerror):
  if (errno != 17): # Exists
    raise

# ------------------------------------------------------------------------
# Helper functions

def clean_input (filename):
  '''
  Strips leading directory information from a filename.
  '''

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
  '''
  Function that handles the backend processing for the index page (i.e. the
  page that lists files in the CWD).
  '''

  # Get session and request QueryDict objects
  s = request.session
  r = request.REQUEST

  # Check to see if the sorting key has been changed in the request
  if ('SortKey' in r):
    sortby = r['SortKey']
    s['SortKey'] = sortby
    # This can be uncommented to make things slightly prettier, but at present
    # needs to be commented for the category anchors to work when the filter
    # links are clicked.
    #return redirect('index')

  # Otherwise, try to load it from the current session (i.e. HTTP cookie)
  elif ('SortKey' in s):
    sortby = s['SortKey']

  # In the final case, set the sorting key to the default
  else:
    sortby = defSortKey
  
  # Create a dictionary to contain information that is to be passed to the
  # HTML template/renderer.
  q = QueryDict('pagetitle=%s'%page_titles['index'])
  q = q.copy()

  # Get the working directory and a list of all the files it contains
  cwd = os.getcwd()
  listing = glob.glob('*')

  matchlist = []

  # Iterates over every file type in the dictionary of regex parsers
  for key, value in redict_auth.iteritems():

    # The "value" variable contains a list of 3 items:
    #  0: An index number for sorting
    #  1: The name used to describe the file type
    #  2: The compiled regular expression object

    # For every file in the current directory, determines if it matches the
    # file type in question (i.e. the entry in the regex dict). If so, adds it
    # to a list "matchobj".
    matchobj = [result for result in [value[2].match(item) for item in listing] if result]

    # The actual filename of the matching object
    matches = [part.group() for part in matchobj]

    # The extracted values from the regular expression
    extras = [part.groupdict() for part in matchobj]

    # Compiles statistics for each filename in "matches"
    # Modification datetime
    modified = [datetime.datetime.fromtimestamp(os.path.getmtime(item)) for item in matches]
    # File size
    size = [os.path.getsize(item) for item in matches]
    # The frequency of the file (if applicable)
    freq = [result['freq'] if ('freq' in result and result['freq'] != '') else None for result in extras]
    # The iteration number of the file (if applicable)
    iteration = [int(result['iter']) if ('iter' in result and result['iter'] != '') else None for result in extras]

    # In order to determine the oldest and youngest files in the list, it is
    # necessary to check all values.  The initial values for the scan are set
    # here ("oldest" is set to the current time).
    youngest = 0
    oldest = int(datetime.datetime.now().strftime('%s'))

    # Based on the modification date, finds the youngest and oldest file
    # Note that the variables "youngest" and "oldest" are in the local scope,
    # so the scale range is set independently for each group of files.
    for item in modified:
      ts = int(item.strftime('%s'))
      if (youngest < ts):
        youngest = ts
      if (oldest > ts):
        oldest = ts

    # The time range between the oldest and youngest files
    stamprange = youngest - oldest

    # Presuming that there is a range of times in the first place, map the
    # files to a range depending on the age of each.  Several situations might
    # prevent this from working (e.g., if the files are on a NFS volume that
    # does not track modification time, or if the files were extracted from an
    # archive w/o preserving the old file metadata).
    if (stamprange != 0):
      freshnesses = [(float(mtime.strftime('%s'))-oldest) / stamprange for mtime in modified]
    else:
      freshnesses = [0. for mtime in modified]

    # Threshold the freshness values (they must be above "freshthresh", which
    # is set at the beginning of the file).  Values that do not qualify are set
    # to None, which makes it simpler to ignore them at the HTML rendering
    # stage.
    freshnesses = [fresh if (fresh > freshthresh) else None for fresh in freshnesses]

    # Create a list of items, each of which comprises a dictionary of metadata
    # corresponding to a file that fits the current filetype.
    # Then, along with the indexing information for the file type itself
    # (i.e., name, id and description), store the list in the parent
    # object "matchlist".
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

  # Update the QueryDict with information needed by the page renderer.
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
  '''
  Function that handles the backend processing for the show (i.e. the page
  that contains a plot).
  '''

  # Form a QueryDict dictionary to store information that goes back to the
  # HTML renderer.
  q = QueryDict('pagetitle=%s'%(page_titles['show']%renderpath))
  q = q.copy()

  # Determine the URLs to render the plot and download the original information
  q['renderpath'] = reverse('render', args=[renderpath])
  q['downloadpath'] = reverse('download', args=[renderpath])

  return render_to_response('show.html', q, context_instance=RequestContext(request))

# ------------------------------------------------------------------------
# File PNG renderer

# Can enable gzip compression, but it doesn't do much for PNG files
# @gzip_page
def view_render (request, filename):
  '''
  Function that produces PNG images for a given filename.
  '''

  # Get a datetime object representing the modification time of the file
  filedt = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
  dirty = True

  # Attempt to get information about the last time the file was rendered
  try:
    # If that information exists, check to see if the file has been modified
    # since the last time it was processed.  If not, change the "dirty" flag
    # to indicate that the cache is (presumed) good.
    rr = RenderResult.objects.get(filename=filename)
    if (rr.lastmodified == filedt):
      dirty = False
  except:
    # Otherwise, there is no known information about the file.  Put together an
    # entry in the database that indicates current information and the place
    # where the cached image file will be stored.
    rr = RenderResult(filename=filename, lastmodified=filedt, requesthash='',diskbuffer='%s/%s.png'%(DIBUPATH, filename))

    # Exactly how to handle simultaneous requests is a tricky question.  This
    # will probably break if the image is requested again before the cache has
    # been filled.  However, holding off on the flag could result in filesystem
    # errors.  Instead, this just has the potential to result in an HTTP 500.
    rr.save()

  if (dirty):
    # The file needs to be rendered
    if (VERBOSE): print('DIRTY: Rendering %s...'%filename)

    # Passes the filename to the handler, which should return a PIL image
    # object containing the plot (or None if there was an error).
    image = handle(clean_input(filename))
    if (image != None):
      # Save the PNG image to the temporary file referenced in the database
      image.save(rr.diskbuffer, 'PNG')

      # Render a response based on the in-memory version
      response = HttpResponse(mimetype='image/png')
      image.save(response, 'PNG')
      return response
    else:
      raise Http404
  else:
    # According to the database, the original file hasn't been modified since
    # the last time a plot was rendered.  The image file should in principle
    # be available from the cache directory.
    if (VERBOSE): print('CLEAN: Reading %s from cache...'%filename)

    # Try to render a response directly from the file buffer, rather than
    # going to the source file. This is usually much quicker and more efficient.
    try:
      fp = open(rr.diskbuffer, 'rb')
      response = HttpResponse(fp, mimetype='image/png')
    except:
      print('Cache miss on rendering %s; stop clicking [Refresh].'%filename)
      raise
    return response

# ------------------------------------------------------------------------
# Non-file meta / project information renderer

def view_meta (request):
  '''
  Function that handles processing for the meta information renderers.
  '''

  # Get session and request QueryDict objects
  s = request.session
  r = request.REQUEST
  q = QueryDict('pagetitle=%s'%page_titles['meta'])
  q = q.copy()

  inidict = readini(PROJNM + '.ini')

  q.update({'projnm': PROJNM})
  q.update(inidict)

  return render_to_response('meta.html', q, context_instance=RequestContext(request))

def view_metarender (request, path):
  '''
  Function that handles rendering images for meta page.
  '''

  s = request.session
  r = request.REQUEST

  if (path == 'geometry'):
    image = helper.geometry_render(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  if (path == 'dirichlet'):
    image = helper.dirichlet_render(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  raise Http404
