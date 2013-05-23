.. waveserv documentation master file, created by
   sphinx-quickstart on Thu Jun 14 13:35:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _intro:

Introduction
============

The :program:`waveserv` program provides a web-based interface designed to simplify monitoring `FULLWV <http://orion.es.uwo.ca/index.php/FULLWV>`_ and `OMEGA <http://orion.es.uwo.ca/index.php/OMEGA>`_.  It is specifically designed for use with this software, but is open-source and may be modified or reused freely.  While :program:`waveserv` is less capable than a full seismic processing suite, it is compatible with a wide variety of devices and web browsers.  It also takes advantage of compression and advanced web techniques to make it very easy to monitor your server/cluster/workstation over a slow Internet connection.

The command-line program :program:`waveserv` indexes all of the relevant files in the OMEGA/FULLWV project directory and provides them to the web browser of your choice.  This could (by default) be a browser on the same computer, or it could be a browser running on a computer half way around the world.  The interface is lightweight, and works fine on laptops, workstations, phones and tablets.  The server interface has been tested on Mac OS X and Linux, but will most likely work on any machine with a functional Python environment.  It is based on the development web server from the `Django Project <http://www.djangoproject.com/>`_.

This package is licensed under the `BSD License <http://www.opensource.org/licenses/BSD-3-Clause>`_ (see project source for details).

The :program:`waveserv` package also makes use of the :py:mod:`pygeo` Python module, and in particular the :py:mod:`pygeo.fullpy` interface for reading *projnm.ini* files and :py:mod:`pygeo.segyread.SEGYFile` interface for reading the SEG-Y format datafiles used by OMEGA/FULLWV.  :py:mod:`pygeo` is released under the `GNU Lesser General Public License <http://www.opensource.org/licenses/lgpl-3.0.html>`_.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   cli
   gui
   development
   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

