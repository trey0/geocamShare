# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

def serverRoot(request):
    return dict(SERVER_ROOT_URL = request.build_absolute_uri('/')[:-1])

from django.conf import settings as settings_
def settings(request):
    return dict(settings = settings_)
