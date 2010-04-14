
from share2.shareCore.search import SearchCore

class SearchGeocam(SearchCore):
    fields = ('name', 'user', 'notes', 'tags', 'uuid')
    timeField = 'maxTime' # FIX: handle features with non-zero time extent
    # pairs (user-facing-field-name, django-field-name)
    fieldAliases = (('user', 'owner__username'),)
