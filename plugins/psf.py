from server.common import *

# Dictionary that controls the page titles
page_titles = {
                'psf':         'Acquisition and Model Geometry',
}
def view_psf (request):
  '''
  Function that handles processing for the meta information renderers.
  '''

  # Get session and request QueryDict objects
  s = request.session
  r = request.REQUEST
  q = QueryDict('pagetitle=%s'%page_titles['psf'])
  q = q.copy()

  return render_to_response('psf.html', q, context_instance=RequestContext(request))

def view_psfrender (request, path):
  '''
  Function that handles rendering images for PSF page.
  '''

  s = request.session
  r = request.REQUEST

  if (path == 'dirichlet'):
    image = helper.dirichlet_render(PROJNM)
    response = HttpResponse(mimetype='image/png')
    image.save(response, 'PNG')
    return response

  raise Http404
