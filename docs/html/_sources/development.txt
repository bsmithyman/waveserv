
.. _devel:

Development
===========

To date, all development of :program:`waveserv` has been by me alone (Brendan Smithyman).  I'd be more than pleased to have someone else interested in the development, so please feel free to send questions, comments or fixes to me at `bsmithyman@eos.ubc.ca <mailto:bsmithyman@eos.ubc.ca>`_.

Main Executable
---------------

The :program:`waveserv` executable is written in Python, and uses :py:mod:`optparse` to generate the :ref:`cli`.  It also creates a minimal database for the :py:mod:`django` test web server on the fly, using a temporary :py:mod:`sqlite3` database to store the settings and data.  It imports the :py:mod:`django.core.management` interface, and uses this to construct a new :py:mod:`django` project in the working directory.  The :py:mod:`pygeo.fullpy` module is used to access the **projnm.ini** file from the working directory, and read the information.  This is stored in the :py:mod:`django` database.  While the current version of the interface does not implement this, there are provisions for storing source and receiver information, which would make it possible to plot sources and receivers over model images (or to create maps and geometry plots).

The vast majority of the web-server code is handled by the :py:mod:`django` test web server, which is called using the :py:mod:`django.core.management` interface near the end of the :program:`waveserv` source.  Unless otherwise specified, temporary files are deleted at the end of the execution.

Server Code
-----------

The main logic of the :program:`waveserv` program is managed by the server-side code in the **server/** directory:

**urls.py**
   This file determines the URL (Uniform Resource Locator) structure of the web-based interface.  This determines which Python function handles each URL (e.g., `</index>`_, `</show/...>`_, `</download/...>`_).

**models.py**
   This file defines the database model for :program:`waveserv`, which is necessary for storing information about the project (i.e., from the **projnm.ini** file).  The database is also used to store information for caching images; if the PNG image for a given geophysical datafile is more up-to-date than the file itself, a cached version is used rather than re-generating the figure.

**views.py**
   This file contains code that deals with most/all of the *web-server* aspects of :program:`waveserv`.  This includes data processing for the listing page, the actual *rendering* of figures, handling downloads, caching, etc.  The intent is for this to include most of the processing that is web-interface specific, and as such it makes heavy use of :py:mod:`django` design techniques.  With the exception of some initial data management code, this file is made up of a series of *views*, which handle the server-side processing for web addresses listed in **urls.py**.

**handlers.py**
   This file contains code that deals with most/all of the *geophysical* aspects of :program:`waveserv`.  This includes processing files, interfacing with geophysical data formats (viz., SEG-Y), generating figures in an abstract sense, and filesystem actions.  The file management is heavily dependent on the :py:mod:`re` module (for *regular expression* parsing); :program:`waveserv` knows how to handle a particular file type because of the lookup tables in this source file.  In principle, this could be used to generate plots separately from the web interface (e.g., for scripted generation of figures in conjunction with document preparation).

**settings.py**
   This file is not actually used by :program:`waveserv` at all, but is required if you wish to test code using the regular :py:mod:`django` test server.

**manage.py**
   This file is not actually used by :program:`waveserv` at all, but is required if you wish to test code using the regular :py:mod:`django` test server.

Media and Templates
-------------------

The web interface is built using the :py:mod:`django` templating language, saved in a series of **\*.html** files in the **templates/** directory.  These control most of the structural aspects of the GUI, and are populated with data using server-side Python scripting.  The visual elements are controlled mainly by a stylesheet stored in the **media/** directory.
