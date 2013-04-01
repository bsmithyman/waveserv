from server.common import *
from server.helper import *
from server.handlers import ftypes, dpi

# Dictionary that controls the page titles
page_titles = {
		'cycleskip':		'Cycle Skip Analysis',
}

# ------------------------------------------------------------------------
# Cycle Skip Functions

figopts_cycleskip = {
	'facecolor':	'w',
	'figsize':	(15,13.3),
}

def offset_image (srcs, recs):
  sx, sy, sz, sw = srcs.T
  rx, ry, rz, rw = recs.T
  sgeom = srcs[:,:3]
  rgeom = recs[:,:3]
  ns = srcs.shape[0]
  nr = recs.shape[0]

  sgeom.shape = (ns, 1, 3)
  rgeom.shape = (1, nr, 3)
  sx.shape = (ns, 1)
  sz.shape = (ns, 1)
  rx.shape = (1, nr)
  rz.shape = (1, nr)

  offsets3d = np.sqrt(((rgeom - sgeom)**2).sum(axis=2))

  offsets2d = np.sqrt((rx - sx)**2 + (rz - sz)**2)

  return offsets3d, offsets2d

def cycleskip_render (projnm, freq, obsfile, estfile):

  from pygeo.fullpy import readini
  inidict = readini(projnm + '.ini')

  srcs = inidict['srcs']
  recs = inidict['recs']

  offsets3d, offsets2d = offset_image(srcs, recs)

  reader = ftypes['utest']
  dobs = reader(obsfile)
  dest = reader(estfile)

  phi = np.angle(dest * dobs.conj())

  fig = Figure(**figopts_cycleskip)

  ax = fig.add_subplot(1,1,1)
  ax.set_title('Phase Error $\phi$ at %3.3f Hz'%(freq,))
  cs = ax.contour(offsets3d.T, colors='k', linewidth=2)
  cl = ax.clabel(cs, inline=True, fmt='%6.0f')
  cs = ax.contour(offsets2d.T, colors='0.5', linewidth=2)
  #cl = ax.clabel(cs, inline=True, fmt='%6.0f')
  im = ax.imshow(phi.real.T, vmin=-np.pi, vmax=np.pi, aspect='auto', cmap=matplotlib.cm.bwr)
  cb = fig.colorbar(im, orientation='horizontal', shrink=0.50)
  cb.set_label('Phase Error (radians)')
  ax.set_ylabel('Receiver')
  ax.set_xlabel('Source')

  canvas = FigureCanvas(fig)
  renderer = canvas.get_renderer()
  renderer.dpi = dpi
  canvas.draw()
  l,b,w,h = [int(item) for item in canvas.figure.bbox.bounds]
  im = Image.fromstring("RGB", (w,h), canvas.tostring_rgb())
  im = auto_crop(im)

  return im

# ------------------------------------------------------------------------
# Cycle Skip Views

def view_cycleskip (request):
  '''
  Function that handles processing for the cycle skip analysis plugin.
  '''

  # Get session and request QueryDict objects
  s = request.session
  r = request.REQUEST
  q = QueryDict('pagetitle=%s'%page_titles['cycleskip'])
  q = q.copy()

  lencut = len(PROJNM) + 6
  obsfiles = glob.glob(PROJNM + '.utobs*')
  estfiles = glob.glob(PROJNM + '.utest*')

  obsfreqs = [float(fn[lencut:]) for fn in obsfiles]
  estfreqs = [float(fn[lencut:]) for fn in estfiles]
  obsfreqs.sort()
  estfreqs.sort()

  validfreqs = []
  for thefreq in estfreqs:
    if (thefreq in obsfreqs):
      validfreqs.append('%3.3f'%(thefreq,))

  if ('frequency' in r):
    freq = r['frequency']
  elif ('frequency' in s):
    freq = s['frequency']
  else:
    try:
      freq = validfreqs[0]
    except IndexError:
      freq = None

  q.update({'frequency': freq, 'validfreqs': validfreqs})

  return render_to_response('cycleskip.html', q, context_instance=RequestContext(request))

def view_cycleskiprender (request, path):
  '''
  Function that handles rendering images for cycle-skip detection.
  '''

  s = request.session
  r = request.REQUEST

  basefreq = float(os.path.splitext(path)[0])
  basefreq_formatted = '%3.3f'%(basefreq,) 
  utobsfile = PROJNM + '.utobs' + basefreq_formatted
  utestfile = PROJNM + '.utest' + basefreq_formatted

  if (os.path.isfile(utobsfile) and os.path.isfile(utestfile)):
    image = cycleskip_render(PROJNM, basefreq, utobsfile, utestfile)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response
  else:
    raise Http404
