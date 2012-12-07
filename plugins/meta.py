from server.common import *

# Dictionary that controls the page titles
page_titles = {
                'meta':         'Meta Information',
}

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

  if (path == 'geometry_xy'):
    image = helper.geometry_render_xy(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  if (path == 'geometry_xz'):
    image = helper.geometry_render_xz(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  if (path == 'dirichlet'):
    image = helper.dirichlet_render(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  raise Http404
