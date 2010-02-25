
from share2.shareCore.views import ViewCore
from share2.shareGeocam.models import Photo
from share2.shareGeocam.search import SearchGeocam

class ViewGeocam(ViewCore):
    def getMatchingFeatures(self, request):
        features = Photo.objects.all()
        query = request.REQUEST.get('q', '')
        if query:
            features = SearchGeocam().searchFeatures(features, query)
        return features

viewSingleton = ViewGeocam()
