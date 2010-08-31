
from share2.shareCore.views import ViewCore
from share2.shareGeocam.models import Photo
from share2.shareGeocam.search import SearchGeocam

class ViewGeocam(ViewCore):
    search = SearchGeocam()
    uploadImageModel = Photo

viewSingleton = ViewGeocam()
