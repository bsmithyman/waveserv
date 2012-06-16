
.. _installation:

Installation
============

:program:`waveserv` can be accessed via `Subversion <http://subversion.apache.org/>`_ using the following command::

   svn co https://skylab.bitsmithy.net/svn/public/waveserv/trunk waveserv-base

This checks out the program source code into a directory called **waveserv-base**, using the SVN *trunk* version.  

.. note:: The *trunk* should always be (more or less) functional, but likely does not include the most up-to-date developments.  For the development version, issue::

      svn co https://skylab.bitsmithy.net/svn/public/waveserv/branches/devel waveserv-devel

   However, note that the development version is not guaranteed to do anything other than possibly melt your computer; use at your own risk.

In order to make :program:`waveserv` available system-wide, you need to add the **waveserv-base** directory to the system search path.  For users of :command:`bash` (Mac OS and Linux default in most cases), add the following to your *~/.bash_profile* or *~/.bashrc* file::

   export PATH="/path/to/waveserv-base:$PATH"

For users of :command:`csh`, add the following to your *~/.cshrc* file::

   setenv PATH "/path/to/waveserv-base:$PATH"


Custom Libraries
----------------

:program:`waveserv` requires the :py:mod:`pygeo` Python module in order to run.  To get a copy, issue the command::

   svn co https://skylab.bitsmithy.net/svn/public/pygeo/trunk pygeo-base

Place the directory *pygeo-base* on your Python search path; in :command:`bash`, this would look something like::

   if [ -n "$PYTHONPATH" ]; then
     export PYTHONPATH="/path/to/pygeo-base:$PYTHONPATH"
   else
     export PYTHONPATH="/path/to/pygeo-base"
   fi

Generic Libraries
-----------------

This requires the following Python libraries installed on the system, and is tested with Python 2.6 or 2.7:

+--------------------+----------------------------------+------------------+
| Package            | Description                      | Minimum Version  |
+====================+==================================+==================+
| python             | Python Interpreter               | Tested with 2.6+ |
+--------------------+----------------------------------+------------------+
| python-numpy       | Numerical Python                 | Untested         |
+--------------------+----------------------------------+------------------+
| python-django      | Django Web Framework             | 1.2              |
+--------------------+----------------------------------+------------------+
| python-matplotlib  | Matlab-like plotting environment | Untested         |
+--------------------+----------------------------------+------------------+

If you are using Linux, I would expect all of the generic libraries to be in the package manager, but if not (e.g. CentOS has terrible Python support) they could be installed using another method like "easy_install".  I have not tested with older versions of numpy and matplotlib, but I'm fairly sure that the Django framework needs to be at minimum v1.2.

.. note:: If you are using Mac OS X (or if you want to use Python on MS Windows), I highly recommend the commercial `EPD (Enthought Python Distribution) <http://www.enthought.com/products/epd.php>`_.  This is free for academic use, and reasonably priced for industry use given the level of support offered.  Additionally, there is a free version that most likely would suffice for casual use.  This can also be extremely handy for poorly-behaved Linux distributions.  Enthought supports Python development and open source.
