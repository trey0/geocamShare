
from share2.shareCore.views import ViewCore
from share2.shareCore.models import Feature
from share2.shareGeocam.search import SearchGeocam

class ViewGeocam(ViewCore):
    search = SearchGeocam()

viewSingleton = ViewGeocam()
