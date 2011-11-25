import re
import os
import numpy as np

# SEG-Y library
from pygeo.segyread import SEGYFile

# Image manipulation
import Image, ImageChops

# Plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.cm

# Database entries that are created on execution of the "waveserv" wrapper
from server.models import Project
project = Project.objects.all()[0]

DEBUG = project.debug
VERBOSE = project.verbose

# Default options for SEG-Y
endian = 'Big'

# Default options for plotting
dpi = 100
figopts = {
	'facecolor':	'w',
	'figsize':	(15,8),
}
figopts_data = {
	'facecolor':	'w',
	'figsize':	(15,24),
}


# Colour map settings for 2-D plots (i.e., with imshow)
panel_plot_options = [{
	'cmap': matplotlib.cm.jet,
},{
	'cmap': matplotlib.cm.jet,
},{
	'cmap': matplotlib.cm.gray,
}]

# Colour and style settings for 1-D plots (i.e., with plot and fill_between)
trace_plot_options = [{
	'color': 'b',
},{
	'color': 'y',
},{
	'color': 'r',
},{
	'color': 'g',
}]

# Colour of the background to be removed automatically
# (enables cropping of the figure canvas)
autocropcolour = (255,255,255)

# ------------------------------------------------------------------------
# Helper functions

def swap (trace):
  return [trace, np.arange(len(trace))]

def spectral_ap (traces):
  '''
  Returns the amplitude and phase of a set of data, given arrays corresponding
  to the real and imaginary components.
  '''

  [real, imag] = traces

  amp = np.sqrt(real**2 + imag**2)
  phase = np.arctan(imag/real)

  return [amp, phase]

def auto_crop(im):
  '''
  Automatic PIL cropping from "Kevin Smith" on www.gossamer-threads.com
  Takes a background colour option (set at the top of the file), and crops
  the image canvas to get rid of excess.
  '''

  if (im.mode != "RGB"):
    im = im.convert("RGB")
  bg = Image.new("RGB", im.size, autocropcolour)
  diff = ImageChops.difference(im, bg)
  bbox = diff.getbbox()
  if bbox:
    return im.crop(bbox)
  return im 

# ------------------------------------------------------------------------
# File access functions

def get_ilog (filename):
  '''
  Parses log files from FULLWV and returns information about the objective
  function (absolute value, relative reduction, +/- perturbation) for each
  iteration.
  '''

  f = open(filename)
  lines = f.readlines()
  f.close()

  # Do the actual parsing
  objective = np.array([float(line.strip().split()[2]) for line in lines if line.find('Objective function:') != -1])
  relative = np.array([float(line.strip().split()[5]) for line in lines if line.find('Relative') != -1])
  minpert = np.array([float(line.strip().split()[-1]) for line in lines if line.find('max(gvp)') != -1])
  maxpert = np.array([float(line.strip().split()[-1]) for line in lines if line.find('min(gvp)') != -1])

  # Form a dictionary containing the results
  logdict = {	'objective':	objective,
		'relative':	relative,
		'minpert':	minpert,
		'maxpert':	maxpert,
  }

  return logdict

def get_segy_time (filename):
  '''
  Reads a SEG-Y file and returns all traces, as well as the sample rate
  (read from the binary header).
  '''

  sf = SEGYFile(filename, endian=endian, verbose=VERBOSE)
  traces = sf.readTraces()

  return [traces, sf.bhead['hdt']]

def get_segy_real (filename):
  '''
  Reads a SEG-Y file and returns all traces without additional metadata.
  '''

  sf = SEGYFile(filename, endian=endian, verbose=VERBOSE)
  traces = sf.readTraces()

  return traces

def get_segy_complex (filename):
  '''
  Reads a SEG-Y file and returns all traces without additional metadata.
  The traces are split into two separate arrays, one each for the real and
  imaginary components of the data.
  '''

  sf = SEGYFile(filename, endian=endian, verbose=VERBOSE)
  real = sf.readTraces(sf.findTraces('trid',1001,1001))
  imag = sf.readTraces(sf.findTraces('trid',1002,1002))

  return [real, imag]

# ------------------------------------------------------------------------

def compile_to_dict (exprdict):
  '''
  Given a dictionary of regular expressions in text form, assembles a
  corresponding dictionary of pre-compiled objects that can be used to
  efficiently parse filenames.
  '''

  # Form a dictionary to contain the regular expression objects
  redict = {}
  for key, value in exprdict.iteritems():
    # Try to insert the project name
    try:
      reentry = re.compile(value[2]%project.projnm)
    # Except for cases in which it doesn't get used
    except TypeError:
      reentry = re.compile(value[2])

    redict[key] = value[:2]+[reentry]

  return redict

# Expressions that match general classes of files
# ALL:  Everything except for certain files that should be excluded
# PROJ: Everything that starts with the project name
expressions_meta = {
	'ALL':	[-2,'All','^[^(graph)][^(reorder)].*[^(\.db)]$'],
        'PROJ':	[-1,'Project','^%s.*'],
}
redict_meta = compile_to_dict(expressions_meta)

# Expressions that should be mutually exclusive
# These regular expressions are used to determine the class of a given file,
# so that it can be classified correctly in a list or plotted/represented
# correctly in a rendering.
expressions_authoritative = {
'ilog':		[0,'Log','^.*\.log.*$'],
'vp':		[1,'Velocity','^%s(?P<iter>[0-9]*)\.vp(?P<freq>[0-9]*\.?[0-9]+)?[^i]*$'],
'qp':		[2,'Attenuation','^%s(?P<iter>[0-9]*)\.qp(?P<freq>[0-9]*\.?[0-9]+)?.*$'],
'vpi':		[3,'iVelocity','^%s(?P<iter>[0-9]*)\.vpi(?P<freq>[0-9]*\.?[0-9]+)?.*$'],
'src':		[4,'Source','^%s\.(new)?src$'],
'gvp':		[5,'Gradient','^%s(?P<iter>[0-9]*)\.gvp[a-z]?(?P<freq>[0-9]*\.?[0-9]+)?.*$'],
# Could make these distinct
#'wave':	'^%s(?P<iter>[0-9]*)\.wave(?P<freq>[0-9]*\.?[0-9]+)?.*$',
#'bwav':	'^%s(?P<iter>[0-9]*)\.bwave(?P<freq>[0-9]*\.?[0-9]+)?.*$',
'utest':	[6,'Data','^%s\.u[td]?[ifoOesrcbt]+(?P<freq>[0-9]*\.?[0-9]+).*$'],
# Could make these distinct
#'gvp':		'^%s(?P<iter>[0-9]*)\.gvp(?P<freq>[0-9]*\.?[0-9]+)[^trfO]*$',
#'gvpr':	'^%s(?P<iter>[0-9]*)\.gvpr(?P<freq>[0-9]*\.?[0-9]+).*$',
#'gvpf':	'^%s(?P<iter>[0-9]*)\.gvpf(?P<freq>[0-9]*\.?[0-9]*).*$',
#'gvpt':	'^%s(?P<iter>[0-9]*)\.gvpt(?P<freq>[0-9]*\.?[0-9]*).*$',
#'gvpO':	'^%s(?P<iter>[0-9]*)\.gvpO(?P<freq>[0-9]*\.?[0-9]*).*$',
'wave':		[7,'Wavefield','^%s(?P<iter>[0-9]*)\.(wave|bwave)(?P<freq>[0-9]*\.?[0-9]+).*$'],
}
redict_auth = compile_to_dict(expressions_authoritative)

# An overarching dictionary is created based on the contents of the meta and
# authoritative dictionaries.
redict = {}
redict.update(redict_meta)
redict.update(redict_auth)

# ------------------------------------------------------------------------
# Figure defines
# Sets the bounding box for certain classes of 2-D figures based on the
# model dimensions.
figextent = (	project.xorig,
		project.xorig + project.dx*project.nx,
		project.zorig + project.dz*project.nz,
		project.zorig)

# ------------------------------------------------------------------------
# File renderers

def render_ilog (logdict, figlabels, plotopts):
  '''
  Renders a 2-D plot of some input data.
  viz. log-scaled amplitude of a semblance panel
  '''

  fig = Figure(**figopts)

  ax = fig.add_subplot(2,2,1)
  ax.plot(logdict['objective'], **plotopts[3])
  ax.set_ylabel(figlabels['obj'])
  ax.set_xlabel(figlabels['x'])
  ax.grid(True)

  ax = fig.add_subplot(2,2,3)
  ax.plot(logdict['relative'], **plotopts[3])
  ax.set_ylabel(figlabels['rel'])
  ax.set_xlabel(figlabels['x'])
  ax.grid(True)

  ax = fig.add_subplot(1,2,2)
  ax.plot(logdict['maxpert'], **plotopts[2])
  ax.plot(logdict['minpert'], **plotopts[0])
  ax.set_ylabel(figlabels['vel'])
  ax.set_xlabel(figlabels['x'])
  ax.grid(True)

  return fig

def render_source (info, figlabels, plotopts):
  '''
  Renders a 2-D plot of all source-signatures, along with a 1-D plot showing:
   - the average of the traces, subsequently normalized
   - the normalized traces, subsequently averaged
  '''

  [traces, dt] = info

  fig = Figure(**figopts)

  if (traces.ndim == 1):
    ax = fig.add_subplot(1,1,1)
    ax.plot(traces, np.arange(len(traces))*(dt/1000.), **plotopts[0])
    ax.invert_yaxis()
    ax.axis('tight')
    ax.set_ylabel(figlabels['y'])
  else:
    ax = fig.add_subplot(1,2,1)

    meantraces = traces.mean(axis=0)
    meantraces = meantraces / abs(meantraces).max()
    normmeantraces = (traces.T / abs(traces).max(axis=1)).mean(axis=1)
    timeaxis = np.arange(traces.shape[1])*(dt/1000.)

    ax.plot(meantraces, timeaxis, label='Average Trace', **plotopts[0])
    ax.fill_betweenx(timeaxis, meantraces, where=meantraces>0, **plotopts[0])

    ax.plot(normmeantraces, timeaxis, label='Normalized Avg.', **plotopts[1])
    ax.fill_betweenx(timeaxis, normmeantraces, where=normmeantraces>0, **plotopts[1])

    ax.invert_yaxis()
    ax.axis('tight')
    ax.set_ylabel(figlabels['y'])

    ax = fig.add_subplot(1,2,2)

    im = ax.imshow(traces.T, aspect='auto', extent=[1,traces.shape[0],traces.shape[1]*dt/1000., 0], **plotopts[2])

    ax.set_ylabel(figlabels['y'])
    ax.set_xlabel(figlabels['x2'])

    #cb = fig.colorbar(im, orientation='vertical')
    #cb.set_label(figlabels['cb'])

  return fig

def render_model_real (traces, figlabels, plotopts):
  '''
  Renders a 2-D plot of a set of real values with the dimensions of the model.
  viz. the velocity model, the 1/Q model
  '''

  if (traces.shape[0] > traces.shape[1]):
    figmode = 'horizontal'
  else:
    figmode = 'vertical'

  fig = Figure(**figopts)

  ax = fig.add_subplot(1,1,1)
  im = ax.imshow(traces.T, extent=figextent, **plotopts[0])
  cb = fig.colorbar(im, orientation=figmode, shrink=0.50)
  cb.set_label(figlabels['cb'])

  return fig

def render_wavefield_complex (traces, figlabels, plotopts):
  '''
  Renders two 2-D plots, representing the real and imaginary components of a
  wavefield with the dimensions of the model.
  viz. the gradient, forward- or backword-propagated wavefield
  '''

  [real, imag] = traces

  if (real.shape[0] > real.shape[1]):
    figmode = 'horizontal'
  else:
    figmode = 'vertical'

  fig = Figure(**figopts)

  if (figmode == 'horizontal'):
    ax = fig.add_subplot(2,1,1)
  else:
    ax = fig.add_subplot(1,2,1)
  ax.set_title('Real')
  im = ax.imshow(real.T, extent=figextent, **plotopts[0])
  cb = fig.colorbar(im, orientation=figmode, shrink=0.50)
  cb.set_label(figlabels['cb'])

  if (figmode == 'horizontal'):
    ax = fig.add_subplot(2,1,2)
  else:
    ax = fig.add_subplot(1,2,2)
  ax.set_title('Imaginary')
  im = ax.imshow(imag.T, extent=figextent, **plotopts[1])
  cb = fig.colorbar(im, orientation=figmode, shrink=0.50)
  cb.set_label(figlabels['cb'])

  return fig

def render_wavefield_complex_ap (traces, figlabels, plotopts):
  '''
  Renders two 2-D plots, representing the log amplitude and phase of a
  wavefield with the dimensions of the model.
  viz. the gradient, forward- or backword-propagated wavefield
  '''

  [amp, phase] = spectral_ap(traces)
  logamp = np.log10(amp)

  if (logamp.shape[0] > logamp.shape[1]):
    figmode = 'horizontal'
  else:
    figmode = 'vertical'

  fig = Figure(**figopts)

  if (figmode == 'horizontal'):
    ax = fig.add_subplot(2,1,1)
  else:
    ax = fig.add_subplot(1,2,1)
  ax.set_title('Phase')
  im = ax.imshow(phase.T, extent=figextent, **plotopts[1])
  cb = fig.colorbar(im, orientation=figmode, shrink=0.50)
  cb.set_label(figlabels['cb'])

  if (figmode == 'horizontal'):
    ax = fig.add_subplot(2,1,2)
  else:
    ax = fig.add_subplot(1,2,2)
  ax.set_title('log Amplitude')
  im = ax.imshow(logamp.T, extent=figextent, **plotopts[0])
  cb = fig.colorbar(im, orientation=figmode, shrink=0.50)
  cb.set_label(figlabels['cb'])

  return fig

def render_utest (traces, figlabels, plotopts):
  '''
  Renders two 2-D plots, representing the phase and log-amplitude of a
  frequency-domain data file.
  viz. utest, utobs, etc.
  '''
  [amp, phase] = spectral_ap(traces)
  logamp = np.log10(amp)

  fig = Figure(**figopts_data)

  ax = fig.add_subplot(2,1,1)
  ax.set_title('Phase')
  im = ax.imshow(phase.T, aspect='auto', **plotopts[1])

  ax = fig.add_subplot(2,1,2)
  ax.set_title('log Amplitude')
  im = ax.imshow(logamp.T, aspect='auto', **plotopts[0])
  cb = fig.colorbar(im, orientation='horizontal', shrink=0.50)
  cb.set_label(figlabels['cb'])

  return fig

# ------------------------------------------------------------------------
# Mappings from file renderers to regular expression entries

# These values are used to label certain classes of plots 
labels = {
	'vp':		{	'cb':	'Velocity (m/s)'},
	'vpi':		{	'cb':	'Imag Velocity (m/s)'},
	'qp':		{	'cb':	'1/Q Attenuation'},
        'field':	{	'cb':	'Pressure Field'},
	'src':		{	'cb':	'Amplitude',
				'y':	'Time (ms)',
				'x2':	'Source No.'},
	'utest':	{	'cb':	'Log Amplitude'},
	'ilog':		{	'x':	'Iteration',
				'obj':	'Objective Function',
				'rel':	'Relative Reduction',
				'vel':	'Velocity Perturbation (m/s)'}
}

# Maps a given file-type key to the function that handles it.  Each function
# takes the filename as an input and returns a result for further processing.
ftypes = {
	'vp':		get_segy_real,
	'vpi':		get_segy_real,
	'qp':		get_segy_real,
	'gvp':		get_segy_complex,
	'gvpr':		get_segy_complex,
	'gvpf':		get_segy_complex,
	'gvpt':		get_segy_complex,
	'gvpO':		get_segy_complex,
	'wave':		get_segy_complex,
	'bwav':		get_segy_complex,
	'src':		get_segy_time,
	'utest':	get_segy_complex,
	'ilog':		get_ilog,
}

# Maps a given file-type key to the function that renders it.  Each function
# takes data (from the functions indexed by "ftypes") as an argument, as well
# as objects containing label text and plotting options.
mappings = {
'vp':	lambda tr: render_model_real(tr, labels['vp'], panel_plot_options[:1]),
'vpi':	lambda tr: render_model_real(tr, labels['vp'], panel_plot_options[:1]),
'qp':	lambda tr: render_model_real(tr, labels['qp'], panel_plot_options[1:2]),

# Version that shows real and imaginary components of the gradient
'gvp':	lambda tr: render_wavefield_complex(tr, labels['field'], panel_plot_options[0:2]),

# Version that shows phase and log amplitude of the gradient
#'gvp':	lambda tr: render_wavefield_complex_ap(tr, labels['field'], panel_plot_options[1:3]),

# Could make these distinct
#'gvpr':	lambda tr: render_wavefield_complex(tr, labels['field']),
#'gvpf':	lambda tr: render_wavefield_complex(tr, labels['field']),
#'gvpt':	lambda tr: render_wavefield_complex(tr, labels['field']),
#'gvpO':	lambda tr: render_wavefield_complex(tr, labels['field']),

# Version that shows real and imaginary components of the wavefield
#'wave':	lambda tr: render_wavefield_complex(tr, labels['field'], panel_plot_options[0:2]),

# Version that shows phase and log amplitude of the gradient
'wave':	lambda tr: render_wavefield_complex_ap(tr, labels['field'], panel_plot_options[1:3]),

#	'bwav':	lambda tr: render_wavefield_complex(tr, labels['field']),
'src':	lambda tr: render_source(tr, labels['src'], trace_plot_options[0:2]+panel_plot_options[2:3]),
'utest':	lambda tr: render_utest(tr, labels['utest'], panel_plot_options[1:3]),
'ilog':	lambda tr: render_ilog(tr, labels['ilog'], trace_plot_options),
}

# ------------------------------------------------------------------------

def handle (filename):
  '''
  Function that dispatches requests to the renderers.
  When a filename is passed to the handle(...) function, it attempts to find
  a match for that filename among the dict of authoritative regular-expressions
  stored in redict_auth.

  Unlike in the index page view, in most cases there will always be a match for
  the filename in question (since the natural way to reach this function is
  via a valid link from the index page).

  The filename is matched against the dictionary of regex parsers, and if there
  is a match, it is fed through the "ftypes" dictionary (which indexes file-
  handling functions).  Presuming that the file is valid, a result will be
  returned, named "traces" (in fact, this is sometimes a more complex object,
  depending on the exact filetype).

  The data is then passed to one of the functions indexed by the "mappings"
  dictionary, based on the filetype regex above.  This (if successful) returns
  a matplotlib figure object, which is in turn used to initialize a
  FigureCanvas object.  The FigureCanvas object is responsible for rendering
  the figure as a PNG image.

  The PNG image is cropped to remove whitespace (or whatever background colour
  is set at the beginning of this source file), and the PNG image is returned
  to the calling function (viz., the render view).
  '''

  for key, value in redict_auth.iteritems():
    matchresult = value[2].match(filename)
    if (matchresult != None):
      try:
        traces = ftypes[key](filename)
      except Exception as errorresult:
        print('Unable to handle file %s as %s.\n%s'%(filename, key, errorresult))
        return None

      try:
        fig = mappings[key](traces)
      except Exception as errorresult:
        print('Unable to generate figure for file %s as %s.\n%s'(filename, key, errorresult))
        return None

      try:
        canvas = FigureCanvas(fig)
      except Exception as errorresult:
        print('Failed to generate FigureCanvas for %s.\n%s'%(filename, errorresult))
        return None

      renderer = canvas.get_renderer()
      renderer.dpi = dpi
      canvas.draw()
      l,b,w,h = [int(item) for item in canvas.figure.bbox.bounds]
      im = Image.fromstring("RGB", (w,h), canvas.tostring_rgb())
      im = auto_crop(im)
  
      return im

  print('Did not find a matching renderer for file %s'%filename)
  return None
