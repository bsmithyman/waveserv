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

DEBUG = project.debug
VERBOSE = project.verbose
DIBUPATH = project.dibupath
PROJNM = project.projnm
