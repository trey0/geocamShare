=========================================
GeoCam Share
=========================================

Requirements
~~~~~~~~~~~~

Our primary development platform for GeoCam Share is Ubuntu Linux 10.04
"Lucid Lemur", with Apache 2.2 running Python 2.6 and Django 1.2 under
modwsgi.

We have also successfully installed parts of GeoCam Share on RedHat
Enterprise Linux 5.5 and Mac OS X 10.6 (Snow Leopard).  However, if you
use these platforms you may need to improvise more during installation.

Installation
~~~~~~~~~~~~

Sorry, these installation instructions are a work in progress.

How to install dependencies on Ubuntu (some of these packages are recommended but not required)::

  sudo apt-get install python-docutils python-imaging python-rdflib python-pip git-core apache2 libapache2-mod-wsgi libimage-exiftool-perl imagemagick python-pyproj
  sudo pip install iso8601 pytz django django-tagging python_digest

  # install django_digest from source (pypi version not compatible with django 1.2) -- http://bitbucket.org/akoha/django-digest/src

  # if using sqlite (good for simple testing)
  sudo apt-get install python-pysqlite2
  # if using mysql (used for production)
  sudo apt-get install mysql-server python-mysqldb

  # not required but recommended for debugging
  sudo apt-get install ipython

How to fetch the GeoCam Share source::

  git clone https://github.com/geocam/geocamShare.git share2

How to install::

  cd share2
  python setup.py install

Note that this is not a standard Python install script -- the action it takes
is more like 'build' than 'install'.  It does not modify anything outside the
current directory.

Further steps, not yet documented:

 * Modify local_settings.py to connect to your database
 * Add server to your Apache config

| __BEGIN_LICENSE__
| Copyright (C) 2008-2010 United States Government as represented by
| the Administrator of the National Aeronautics and Space Administration.
| All Rights Reserved.
| __END_LICENSE__
