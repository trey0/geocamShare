
from share2.shareCore.views import ViewCore
from share2.shareGeocam.models import Photo

class ViewGeocam(ViewCore):
    def getAllFeatures(self):
        return Photo.objects.all()

viewSingleton = ViewGeocam()
