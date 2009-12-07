
def serverRoot(request):
    return dict(SERVER_ROOT_URL = request.build_absolute_uri('/'))

from django.conf import settings as settings_
def settings(request):
    return dict(settings = settings_)
