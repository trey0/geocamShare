=========================================
GeoCam Share Tracking Module
=========================================

.. sectnum::

.. contents:: Contents

About
~~~~~

The tracking module is currently (Oct 2010) a prototype of how we could
handle tracking live resource positions using GeoCam Share.  The intent
is to add a matching position posting feature to GeoCam Mobile, and we
could also accept position info from other sources.

Installation
~~~~~~~~~~~~

Follow the normal directions for installing GeoCam Share.  If you're
updating an existing install, you'll need to run ``./manage.py syncdb``
to add the new DB tables.

To see the prototype display, load http://localhost:8000/tracking/liveMap/
or the corresponding URL on your server.  Initially, the map won't have
any markers.

To add some markers and simulate movement, run
``shareTracking/clientSim.py -s 100 -v``.  This simulates five clients
driving around at 100 km/h and posting independent position updates at
about 1 Hz each.  (This live map is designed to be engaging. Note that
real clients will probably post updates at most once every 30 seconds.)

Currently, the database only stores the most recent position update for
each resource.  Later, we'll want to have some capability to store and
display tracks as well.  We'll also want the display integrated with
the existing GeoCam Share map interface.

If you'd like to see the data format the simulated clients are posting
in, you can run clientSim with the ``-vv`` option.

| __BEGIN_LICENSE__
| Copyright (C) 2008-2010 United States Government as represented by
| the Administrator of the National Aeronautics and Space Administration.
| All Rights Reserved.
| __END_LICENSE__

