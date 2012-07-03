import numpy as np

# Image manipulation
import Image, ImageChops

# Plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.cm
import matplotlib.pylab as pl

# Colour of the background to be removed automatically
# (enables cropping of the figure canvas)
autocropcolour = (255,255,255)
dpi = 100

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
# Dirichlet kernel renderer

# Settings for dirichlet
def_samps = 1000
def_ymax = 100000

figopts_dirichlet = {
	'facecolor':	'w',
	'figsize':	(15,8),
}

def dirichlet_gauleg (m):
  n = (m-1)*2 + 1
  x = np.zeros((m,))
  w = np.zeros((m,))
  eps = 1E-5

  for i in xrange(1,m+1):
    z = np.cos(np.pi*(i-0.25)/(n+0.5))

    while (True):
      p1 = 1.0
      p2 = 0.0
      for j in xrange(1,n+1):
        p3 = p2
        p2 = p1
        p1 = ((2.*j - 1.)*z*p2 - (j-1)*p3)/j

      pp = n*(z*p1 - p2)/(z**2 - 1.)
      z1 = z
      z = z1 - p1/pp
      if (abs(z-z1) <= eps):
        break

    x[m-i] = z
    w[m-i] = 2./((1. - z*z)*pp**2)

  return x, w

def dirichlet_kernel (y, kys, weights):
  print 'test2'
  print kys
  

  outseries = 0.5*dirichlet_kernel(kys[0], y)*weights[0]
  for i, ky in enumerate(kys[1:]):
    outseries += np.cos(ky * y) * weights[i+1]

  return outseries

def dirichlet_comparison (y, nky, vmin, omega):
  kc = omega/vmin

  linx = np.linspace(0, kc, nky)
  linw = np.ones_like(linx) / nky
  linkernel = dirichlet_kernel(y, linx, linw)

  gaux, gauw = dirichlet_gauleg(nky)
  gaux *= kc
  gaukernel = dirichlet_kernel(y, gaux, gauw)

  return linkernel, gaukernel

def dirichlet_render (projnm):

  from pygeo.fullpy import readini
  inidict = readini(projnm + '.ini')

  # Decide what the maximum y-difference is and scale accordingly
  itemlist = ['srcs','recs','geos']
  for item in itemlist:
    if (inidict[item].shape[0] == 0):
      itemlist.remove(item)
  
  ymax = max((inidict[item][:,1].max() for item in itemlist))
  ymin = min((inidict[item][:,1].min() for item in itemlist))
  ydiff = ymax - ymin

  # Get existing ky information
  kys = inidict['kys']
  method = inidict['method']
  nky = inidict['nky']
  vmin = inidict['vmin']
  freqs = inidict['freqs']


  # Define basis for plot
  y = np.linspace(0, def_ymax, def_samps)

  minomega = freqs.min()
  maxomega = freqs.max()

  fig = Figure(**figopts_dirichlet)
  print 'test1'
  kysw = np.ones_like(kys) / nky
  ex = dirichlet_kernel(y, kys, kysw)
  print 'test3'
  lk1, gk1 = dirichlet_comparison(y, nky, vmin, minomega)
  lk2, gk2 = dirichlet_comparison(y, nky, vmin, maxomega)

  ax = fig.add_subplot(2,1,1)
  ax.plot(y, ex, 'r-', label='Current')
  ax.plot(y, lk1, 'b-', label='Linear')
  ax.plot(y, gk1, 'g-', label='Gauss-Legendre')
  ax.set_ylabel('Amplitude')
  ax.set_xlabel('Cross-line Distance (m)')
  ax.set_title('Minimum $\omega$: %f'%(minomega,))
  ax.legend()

  ax = fig.subplot(2,1,2)
  ax.plot(y, ex, 'r-', label='Current')
  ax.plot(y, lk2, 'b-', label='Linear')
  ax.plot(y, gk2, 'g-', label='Gauss-Legendre')
  ax.ylabel('Amplitude')
  ax.xlabel('Cross-line Distance (m)')
  ax.title('Maximum $\omega$: %f'%(maxomega,))
  ax.legend()

  canvas = FigureCanvas(fig)
  renderer = canvas.get_renderer()
  renderer.dpi = dpi
  canvas.draw()
  l,b,w,h = [int(item) for item in canvas.figure.bbox.bounds]
  im = Image.fromstring("RGB", (w,h), canvas.tostring_rgb())
  im = auto_crop(im)

  return im

