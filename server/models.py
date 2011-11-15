from django.db import models

class Project (models.Model):
  '''
  Data class that stores information from the "waveserv" wrapper (much of which
  is extracted from the projnm.ini file.
  '''

  projnm = models.CharField(max_length=40)
  dibupath = models.CharField(max_length=128)
  debug = models.BooleanField()
  verbose = models.BooleanField()
  nx = models.IntegerField()
  nz = models.IntegerField()
  dx = models.FloatField()
  dz = models.FloatField()
  xorig = models.FloatField()
  zorig = models.FloatField()
  dt = models.FloatField()
  ns = models.IntegerField()
  nr = models.IntegerField()
  ng = models.IntegerField()

  def __unicode__(self):
    return '%s: %dx%d, %fx%f, (%f,%f)'%(self.projnm, self.nx, self.nz, self.dx, self.dz, self.xorig, self.zorig)

class ShotPoint (models.Model):
  '''
  Data class for a shotpoint record.
  '''

  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  swght = models.FloatField()

class ReceiverPoint (models.Model):
  '''
  Data class for a receiver record.
  '''

  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  rwght = models.FloatField()

class GeophonePoint (models.Model):
  '''
  Data class for a geophone record.
  '''

  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  gwght = models.FloatField()

class RenderResult (models.Model):
  '''
  Data class that stores information about a given result from rendering a
  plot.  This is used to provide a cache of pre-rendered images for situations
  when the same file is requested multiple times (but has not changed in the
  interim).  There is also provision for additional settings to be passed in
  the request, which would invalidate the stored "requesthash" and trigger a
  new render.
  '''

  filename = models.CharField(max_length=100)
  lastmodified = models.DateTimeField()
  requesthash = models.CharField(max_length=30)
  diskbuffer = models.CharField(max_length=100)

  def __unicode__(self):
    return '%s - %s'%(self.filename, self.diskbuffer)
