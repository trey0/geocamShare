
from share2.shareCore.search import SearchCore
from share2.shareCore.models import Feature

class SearchGeocam(SearchCore):
    getAllFeatures = Feature.objects.all
    fields = ('name', 'user', 'notes', 'tags', 'uuid')
    timeField = 'maxTime' # FIX: handle features with non-zero time extent
    # pairs (user-facing-field-name, django-field-name)
    fieldAliases = (('user', 'author__username'),)
