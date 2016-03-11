import numpy as np

# Image manipulation
from PIL import Image, ImageChops

# Plotting
import matplotlib
matplotlib.use('agg')
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.cm
import matplotlib.pylab as pl
import matplotlib.patches as mpatches

# Database entries that are created on execution of the "waveserv" wrapper
from server.models import Project
project = Project.objects.all()[0]

# ------------------------------------------------------------------------
# Figure defines
# Sets the bounding box for certain classes of 2-D figures based on the
# model dimensions.
figextent = (	project.xorig,
		project.xorig + project.dx*(project.nx-1),
		project.zorig + project.dz*(project.nz-1),
		project.zorig)

pfigextent = (figextent[0], figextent[1], -figextent[2], -figextent[3])

# Colour of the background to be removed automatically
# (enables cropping of the figure canvas)
autocropcolour = (255,255,255)
dpi = 100

# ------------------------------------------------------------------------
# Helper functions

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

def spectral_ap (traces):
  '''
  Returns the amplitude and phase of a set of data, given arrays corresponding
  to the real and imaginary components.
  '''

  amp = np.abs(traces)
  phase = np.angle(traces)

  return [amp, phase]

def swap (trace):
  return [trace, np.arange(len(trace))]
