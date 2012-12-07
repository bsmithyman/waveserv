from server.common import *
from server.helper import *

# Dictionary that controls the page titles
page_titles = {
                'geom':         'Acquisition and Model Geometry',
}

# ------------------------------------------------------------------------
# Geometry renderer

# Settings for geometry

figopts_geometry = {
	'facecolor':	'w',
	'figsize':	(15,8),
}

def geometry_render_xy (projnm):

  from pygeo.fullpy import readini
  inidict = readini(projnm + '.ini')

  # Get existing ky information
  srcs = inidict['srcs']
  recs = inidict['recs']
  geos = inidict['geos']

  fig = Figure(**figopts_geometry)

  axy = fig.add_subplot(1,1,1, aspect=1.0, adjustable='box')
  axy.yaxis.set_major_formatter(FormatStrFormatter('%+d'))

  if (srcs.shape != (0,)):
    axy.plot(srcs[:,0], srcs[:,1], 'r,', label='Sources')

  if (recs.shape != (0,)):
    axy.plot(recs[:,0], recs[:,1], 'g,', label='Hydrophones')

  if (geos.shape != (0,)):
    axy.plot(geos[:,0], geos[:,1], 'b,', label='Geophones')

  #axy.legend()
  axy.set_ylabel('Offline Coordinate (m)')
  axy.set_xlabel('Line Location (m)')
  axy.set_title('Plan View')

  #currentyaxis = axy.axis()
  #axy.axis((figextent[0], figextent[1], currentyaxis[2], currentyaxis[3]))

  canvas = FigureCanvas(fig)
  renderer = canvas.get_renderer()
  renderer.dpi = dpi
  canvas.draw()
  l,b,w,h = [int(item) for item in canvas.figure.bbox.bounds]
  im = Image.fromstring("RGB", (w,h), canvas.tostring_rgb())
  im = auto_crop(im)

  return im

# ------------------------------------------------------------------------

def geometry_render_xz (projnm):

  from pygeo.fullpy import readini
  inidict = readini(projnm + '.ini')

  # Get existing ky information
  srcs = inidict['srcs']
  recs = inidict['recs']
  geos = inidict['geos']

  fig = Figure(**figopts_geometry)

  axz = fig.add_subplot(1,1,1, aspect=1.0, adjustable='box')
  axz.yaxis.set_major_formatter(FormatStrFormatter('%+d'))

  if (srcs.shape != (0,)):
    axz.plot(srcs[:,0], -srcs[:,2], 'r,', label='Sources')

  if (recs.shape != (0,)):
    axz.plot(recs[:,0], -recs[:,2], 'g,', label='Hydrophones')

  if (geos.shape != (0,)):
    axz.plot(geos[:,0], -geos[:,2], 'b,', label='Geophones')

  print figextent
  axz.plot([pfigextent[0],pfigextent[0],pfigextent[1],pfigextent[1]],
           [pfigextent[2],pfigextent[3],pfigextent[3],pfigextent[2]],
           'k:')#figopts_geometry['facecolor'])

  rect = mpatches.Rectangle((figextent[0],-figextent[2]), figextent[1]-figextent[0], -figextent[3] + figextent[2] , edgecolor='k', fill=False)
  axz.add_patch(rect)

  #axz.legend()
  axz.set_ylabel('Elevation (m)')
  axz.set_xlabel('Line Location (m)')
  axz.set_title('Cross Section')

  #ax.axis(figextent)
  #axz.axis('scaled')
  axz.axis(pfigextent)

  canvas = FigureCanvas(fig)
  renderer = canvas.get_renderer()
  renderer.dpi = dpi
  canvas.draw()
  l,b,w,h = [int(item) for item in canvas.figure.bbox.bounds]
  im = Image.fromstring("RGB", (w,h), canvas.tostring_rgb())
  im = auto_crop(im)

  return im

# ------------------------------------------------------------------------
# Geometry Views

def view_geom (request):
  '''
  Function that handles processing for the geom information renderers.
  '''

  # Get session and request QueryDict objects
  s = request.session
  r = request.REQUEST
  q = QueryDict('pagetitle=%s'%page_titles['geom'])
  q = q.copy()

  inidict = readini(PROJNM + '.ini')

  q.update({'projnm': PROJNM})
  q.update(inidict)

  return render_to_response('geom.html', q, context_instance=RequestContext(request))

def view_geomrender (request, path):
  '''
  Function that handles rendering images for geom page.
  '''

  s = request.session
  r = request.REQUEST

  if (path == 'geometry_xy'):
    image = geometry_render_xy(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  if (path == 'geometry_xz'):
    image = geometry_render_xz(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

