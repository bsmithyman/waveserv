from django.db import models

class Project (models.Model):
  projnm = models.CharField(max_length=40)
  dibupath = models.CharField(max_length=128)
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
  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  swght = models.FloatField()

class ReceiverPoint (models.Model):
  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  rwght = models.FloatField()

class GeophonePoint (models.Model):
  x = models.FloatField()
  y = models.FloatField()
  z = models.FloatField()
  gwght = models.FloatField()

class RenderResult (models.Model):
  filename = models.CharField(max_length=100)
  lastmodified = models.DateTimeField()
  requesthash = models.CharField(max_length=30)
  diskbuffer = models.CharField(max_length=100)

  def __unicode__(self):
    return '%s - %s'%(self.filename, self.diskbuffer)
