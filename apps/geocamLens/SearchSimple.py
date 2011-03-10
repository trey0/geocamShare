# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from geocamCore.models import PointFeature

from geocamLens.SearchAbstract import SearchAbstract

class SearchSimple(SearchAbstract):
    def getAllFeatures(self):
        return PointFeature.objects.filter(processed=True)

    fields = ('name', 'user', 'notes', 'tags', 'uuid')
    timeField = 'timestamp' # FIX: handle features with non-zero time extent
    # pairs (user-facing-field-name, django-field-name)
    fieldAliases = (('user', 'author__username'),)
