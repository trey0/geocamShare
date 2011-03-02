=========================================
GeoCam Share Installation
=========================================

These installation instructions are a work in progress.  If you follow
the directions and run into problems, let us know!

We will go through two versions of the installation:

1. Basic installation using Django's built-in development web server and
   a SQLite database.  This version is only suitable for quick testing due
   to security and performance issues.

2. Advanced installation using the Apache web server and a MySQL
   database.  This version is intended for real deployments.

Requirements
~~~~~~~~~~~~

Our primary development platform for GeoCam Share is Ubuntu Linux 10.04
(Lucid Lemur), running Python 2.6 and Django 1.2.  For the basic
installation we use Django's built-in development web server with a
SQLite 3.6 database.  For the advanced installation we use the Apache
2.2 web server hosting Python using mod_wsgi 2.8, with a MySQL 5.1
database.

We have also successfully installed parts of GeoCam Share on RedHat
Enterprise Linux 5.5, Mac OS X 10.6 (Snow Leopard), and an Ubuntu
virtual machine running under VMWare on a Windows host.  However, we do
not officially support those platforms.  Our installation instructions
below mostly assume Ubuntu, so if you want to use another platform you
may need to improvise more during installation.

Set Up an Install Location
~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's create a directory to hold the whole Share installation
and capture the path in an environment variable we can use
in the instructions below::

  export GEOCAM_DIR=$HOME/projects/geocam # or choose your own
  mkdir -p $GEOCAM_DIR

Get the Source
~~~~~~~~~~~~~~

Visit the `GeoCam Share repository on GitHub`_, click on the Downloads_
button, and click on "Download .tar.gz" to get a tarball.  Then drop the
tarball into the ``$GEOCAM_DIR`` directory and run::

  cd $GEOCAM_DIR
  tar xfz geocam-geocamShare-*.tar.gz
  # rename the resulting directory to "geocamShare"
  mv `ls -d geocam-geocamShare-* | head -1` geocamShare

.. _GeoCam Share repository on GitHub: http://github.com/geocam/geocamShare/
.. _Downloads: http://github.com/geocam/geocamShare/archives/master

**Advanced version:** If you're interested in contributing code to GeoCam
Share, you can check out our latest revision with::

  cd $GEOCAM_DIR
  git clone http://github.com/geocam/geocamShare.git geocamShare

For more information on the Git version control system, visit `the Git home page`_.
You can install Git on Ubuntu with::

  sudo apt-get install git-core

.. _the Git home page: http://git-scm.com/

Optionally Install virtualenv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Especially for a quick test install, we recommend using the virtualenv_
tool to put Share-related Python packages in an isolated sandbox where
they won't conflict with other Python tools on your system.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

To install virtualenv, create a sandbox named ``packages``, and
"activate" the sandbox::

  sudo apt-get install python-virtualenv
  cd $GEOCAM_DIR
  virtualenv packages
  source packages/bin/activate

After your sandbox is activated, package management tools such as
``easy_install`` and ``pip`` will install packages into your sandbox
rather than the standard system-wide Python directory, and the Python
interpreter will know how to import packages installed in your sandbox.

You'll need to source the ``activate`` script every time you log in
to reactivate the sandbox.

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

First install Ubuntu packages::

  # tools for Python package compilation and management
  sudo apt-get install python2.6-dev python-pip

  # basic database
  sudo apt-get install sqlite3 libsqlite3-dev
  
  # rendering icons and reading image metadata
  sudo apt-get install libjpeg-dev libimage-exiftool-perl imagemagick

Then install Python dependencies.  For this command to work, you will
either need to make sure your virtualenv environment is activated (as
explained above, recommended) or run with ``sudo``::

  pip install -r $GEOCAM_DIR/geocamShare/make/pythonRequirements.txt

Set Up GeoCam Share
~~~~~~~~~~~~~~~~~~~

To render icons and collect media for the server, run::

  cd $GEOCAM_DIR/geocamShare
  python setup.py install

Note that, maybe confusingly, this is not a standard Python install
script.  The action it takes is more like "build" than "install".  It
does not modify anything outside the ``geocamShare`` directory.

To set up your shell environment to run Share::

  source $GEOCAM_DIR/geocamShare/sourceme.sh

You'll need to source the ``sourceme.sh`` file every time you open a new
shell if you want to run Share-related Python scripts such as starting
the Django development web server.  The ``sourceme.sh`` file will also
take care of activating your virtualenv environment in new shells (if
you were in a virtualenv when you ran ``setup.py``).

To initialize the database::

  $GEOCAM_DIR/geocamShare/manage.py syncdb

The syncdb script will ask you if you want to create a Django superuser.
We recommend answering 'yes' and setting the admin username to ``root``
for compatibility with our utility scripts.

Import Sample Data
~~~~~~~~~~~~~~~~~~

To download and import 37 sample photos::

  cd $GEOCAM_DIR
  curl http://geocamshare.org/downloads/geocamShareSampleData.tar.gz -O
  tar xfz geocamShareSampleData.tar.gz
  python geocamShare/shareGeocam/simpleImport.py --user root geocamShareSampleData

You can also clean out all the photos in the database by running
``simpleImport.py`` with the ``-c`` "clean" option.  This is handy if
there's a problem and you want to try importing the sample data again.

Try It Out
~~~~~~~~~~

To run the Django development web server::

  $GEOCAM_DIR/geocamShare/manage.py runserver

Now you're ready to try it out!  If you can open a web browser on the
same host where Share is installed, you can start using the app by
visiting http://localhost:8000/ in that browser.

Connecting to the Django Development Web Server From a Remote Host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For security, the Django development web server only accepts connections
from the host where it is running.  Let's suppose the host you're
sitting at is called ``myclient`` and the host running Share is called
``myserver``.  Here are some workarounds you can use to connect to the
app from a remote host:

1. Quick and **insecure**.  Use a different command to start the Django
   development web server, telling it to accept connections from outside
   hosts::

     $GEOCAM_DIR/geocamShare/manage.py runserver 0.0.0.0:8000

   then visit http://myserver:8000/ in your browser.

2. Use an SSH tunnel.  On ``myclient``, run the following to open up a
   secure SSH tunnel to ``myserver``, so that your browser's request
   will appear to come from ``myserver``::

     ssh -L 8000:localhost:8000 myserver -N

   then visit http://localhost:8000/ in your browser.

   Those instructions assume you have a command-line SSH available on
   ``myclient``, but you can also open up tunnels with graphical SSH
   clients on Windows and Mac; check the help for your client.

3. Use remote desktop software to start up a desktop session on
   ``myserver`` so that you can run a browser there, then visit
   http://localhost:8000/ .  This approach won't work as well as an SSH
   tunnel over a slow network connection, but might have other
   advantages.  There are many remote desktop solutions to choose from.
   The VNC protocol is commonly used -- for more information, see the
   `documentation on VNC for Ubuntu`_.

.. _documentation on VNC for Ubuntu: https://help.ubuntu.com/community/VNC

Advanced Installation
~~~~~~~~~~~~~~~~~~~~~

These advanced installation instructions explain how to set up Share for
a production environment using the standard Apache/MySQL web stack.  We
assume you've already gone through the basic installation instructions
above.

We'll just cover the minimal steps you need to install the web stack on
Ubuntu and get it to serve the Share app.  We won't spend much time
talking about how to manage your web stack, which is very important for
a real deployment.  There's lots of reference material for that
available on the web.

Advanced Installation: Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install the Apache/MySQL Ubuntu packages::

  # Apache and mod_wsgi Python hosting environment
  sudo apt-get install apache2 libapache2-mod-wsgi

  # MySQL
  sudo apt-get install mysql-server

During installation of the MySQL package you should be prompted to enter
a password for the MySQL root user.  We'll refer to that password as
``MYSQL_ROOT_PASSWORD`` below.  The `Ubuntu MySQL docs`_ have more
information.

.. _Ubuntu MySQL docs: https://help.ubuntu.com/10.04/serverguide/C/mysql.html

Then install the Python MySQL driver.  For this command to work, you
will either need to make sure your virtualenv environment is activated
(as explained above) or run with ``sudo``::

  pip install MySQL-python==1.2.2

Advanced Installation: Initialize MySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To tell Share to use MySQL as its database, add the following to your
``geocamShare/local_settings.py`` file.  This overrides the default setting
to use a SQLite database::

  DATABASES = {
      'default': {
          'ENGINE': 'mysql',
          'NAME': 'geocamShare',
          'USER': 'root',
          'PASSWORD': 'MYSQL_ROOT_PASSWORD',
          'HOST': '127.0.0.1'
      },
  }

To initialize the MySQL ``geocamShare`` database::

  mysqladmin -u root -p create geocamShare
  $GEOCAM_DIR/geocamShare/manage.py syncdb

Next, you should import some sample data for testing, following the
instructions above.

Advanced Installation: Configure Web Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before configuring Apache to load Share, we recommend adjusting its
settings so that it only accepts connections from ``localhost``.  This
will provide a safer environment in which to do our setup and test
the installation before opening it up to external threats.

In the file ``/etc/apache2/ports.conf``, edit the ``Listen`` line to
the following::

  Listen 127.0.0.1:80

Now tell Apache how to start Share by copying Share config files to a
location where Apache will load them::

  sudo cp $GEOCAM_DIR/build/apache2/*.conf /etc/apache2/conf.d/

By default, Share requires users to log in before they can use the app.
Internet best practices require passwords to be sent over the network
encrypted (using SSL).  If your Apache server does not already support
SSL, you can set it up with::

  sudo apt-get install apache2-ssl-certificate

For more information on generating SSL certificates, see: link1_ link2_.

.. _link1: http://onlamp.com/pub/a/onlamp/2008/03/04/step-by-step-configuring-ssl-under-apache.html

.. _link2: http://ubuntuforums.org/archive/index.php/t-4466.html

Note: The command above installs a `self-signed certificate`_, which is
not ideal.  Because the certificate is self-signed, your users' web
browser cannot confirm the identity of your server, and a malicious host
could pretend to be your server and steal user passwords.  Most web
browsers will also give your users a nasty security warning when they
try to connect.

To avoid these problems in a production environment, you'll need to pay
a `certificate authority`_ to sign your certificate, a fairly complicated
process we won't go into.

.. _certificate authority: http://en.wikipedia.org/wiki/Certificate_authority

If you want to skip past all the security setup, for testing purposes
only, you can edit ``$GEOCAM_DIR/geocamShare/local_settings.py`` and set::

  SECURITY_REDIRECT_ENABLED = False

.. _self-signed certificate: http://en.wikipedia.org/wiki/Self-signed_certificate

Advanced Installation: Try It Out
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Restart Apache to load the new configuration::

  sudo apache2ctl restart

Now you're ready to try out it out!  You should now be able to access
your Share installation at http://myserver/share/ .  

We recommend doing some testing to make sure you understand your
security settings in terms of what anonymous and registered users can
access before opening up your server to outside connections for real
usage.

Advanced Installation: Administration and Adding Users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can perform many Share administrative functions using the Django admin interface
located at http://myserver/share/admin/ .

One vital function is to add user accounts.  In the admin interface,
find the ``Users`` row and click ``Add``.  You'll be prompted for the
new user's username and password.  Once the user is created, you'll be
taken to an editing interface where you can enter additional information
such as name and email address.  In the ``Permissions`` section, you can
give the user ``Staff status``, which allows them to view the admin
interface, or ``Superuser status``, which allows them to edit the
database and manage user accounts.

Unfortunately, we don't currently provide an interface for users to change
their own user profile information, including their password.

Advanced Installation: Multiple Instances of Share On the Same Host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Share is designed to support running multiple instances sharing the same
host and potentially the same Apache and MySQL servers.  You might want
to do this if you are testing different configurations of Share.  To do
this:

1. Unpack and build two copies of Share in different directories.

2. The Django database settings are in ``local_settings.py``, as
   explained above.  You can set your instances of Share to use the same
   MySQL server and create multiple databases with different names
   (change the ``NAME`` field), or have them connect to different MySQL
   servers on different ports (add a colon and port number to the
   ``HOST`` field).

3. The ``/share/`` path suffix in the URL is set using the
   ``DJANGO_SCRIPT_NAME`` field in the ``sourceme.sh`` file.  If you want
   your instances of Share to run on the same web server, you can avoid URL
   conflicts by giving them distinct ``DJANGO_SCRIPT_NAME`` settings.

4. Apache's instructions for loading Share are in the
   ``httpd-geocamShare.conf`` file, which we installed above.  If you're
   running multiple instances of Share on the same Apache server, you'll
   want two different versions of that file in the
   ``/etc/apache2/conf.d/`` directory, one for each instance.

   Run ``python setup.py install`` again after changing
   ``DJANGO_SCRIPT_NAME`` to regenerate the ``.conf`` files. The
   auto-generated version should be mostly correct, but you'll want to
   make sure that the mod_wsgi process group settings are different.  By
   default, the process group is set to your username plus Share (for
   example username ``trey`` gets process group ``treyShare``).  You can
   global search-and-replace the process group in one of the files if
   needed.

   Regardless of how many Share instances you run, you only need one copy
   of the ``httpd-geocamShare-mimetypes.conf`` file per web server.

| __BEGIN_LICENSE__
| Copyright (C) 2008-2010 United States Government as represented by
| the Administrator of the National Aeronautics and Space Administration.
| All Rights Reserved.
| __END_LICENSE__
