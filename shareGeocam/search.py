
from share2.shareCore.search import SearchCore

class SearchGeocam(SearchCore):
    fields = ('name', 'user', 'notes', 'tags', 'uuid')
    timeField = 'timestamp'
    # pairs (user-facing-field-name, django-field-name)
    fieldAliases = (('user', 'owner__username'),)
