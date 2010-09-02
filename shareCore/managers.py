# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import itertools
from operator import attrgetter

from django.db import models
import django.core.exceptions

REPR_OUTPUT_SIZE = 20

class ChainQuerySet:
    """ChainQuerySet is modeled on Django QuerySet but runs the same
    query on multiple derived classes of the same abstract parent class
    and chains the results together.

    Specify the parent model as the MODEL argument and a list of child
    classes as the CLASSES argument to the constructor.

    We only support a small subset of the QuerySet methods, and we
    haven't tried to optimize memory use.  Speed should be ok."""

    def __init__(self, model, classes):
        self._query = models.Q()
        self.model = model
        self._classes = classes
        self._resultCache = None
        self._distinct = False
        self._orderBy = ''
        self._selectRelated = None

    def __iter__(self):
        self._evalQuery()
        for result in self._resultCache:
            yield result

    def __len__(self):
        self._evalQuery()
        return len(self._resultCache)

    def __repr__(self):
        data = self[:REPR_OUTPUT_SIZE + 1]
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)

    def __getitem__(self, k):
        self._evalQuery()
        return self._resultCache.__getitem__(k)

    def _clone(self):
        c = ChainQuerySet(self.model, self._classes)
        for name, val in vars(self).iteritems():
            setattr(c, name, getattr(self, name))
        c._resultCache = None
        return c

    def _evalQuery(self):
        if not self._resultCache:
            subQueries = []
            for c in self._classes:
                qs = c._default_manager.get_query_set().filter(self._query)
                if self._distinct:
                    qs = qs.distinct()
                if self._selectRelated:
                    srFields, srKwargs = self._selectRelated
                    qs = qs.select_related(*srFields, **srKwargs)
                subQueries.append(qs)
            self._resultCache = list(itertools.chain(*subQueries)) # flatten
            if self._orderBy:
                if self._orderBy[0] == '-':
                    reverse = True
                    keyField = self._orderBy[1:]
                else:
                    reverse = False
                    keyField = self._orderBy
                self._resultCache.sort(key=attrgetter(keyField), reverse=reverse)

    def filter(self, *args, **kwargs):
        return self._filterOrExclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        return self._filterOrExclude(True, *args, **kwargs)

    def _filterOrExclude(self, negate, *args, **kwargs):
        c = self._clone()
        if negate:
            c._query = c._query & (~models.Q(*args, **kwargs))
        else:
            c._query = c._query & models.Q(*args, **kwargs)
        return c

    def distinct(self, true_or_false=True):
        c = self._clone()
        c._distinct = true_or_false
        return c

    def order_by(self, *field_names):
        assert len(field_names) == 1, 'ChainQuerySet order_by() only supports a single field, sorry'
        c = self._clone()
        c._orderBy = field_names[0]
        return c

    def select_related(self, *fields, **kwargs):
        c = self._clone()
        c._selectRelated = (fields, kwargs)
        return c

    def get(self, *args, **kwargs):
        self._evalQuery()
        num = len(self._resultCache)
        if num == 1:
            return self._resultCache[0]
        elif num == 0:
            raise django.core.exceptions.ObjectDoesNotExist('%s matching query does not exist'
                                           % self.model._meta.object_name)
        else:
            raise django.core.exceptions.MultipleObjectsReturned("get() returned more than one %s -- it returned %s! Lookup parameters were %s"
                                                                 % (self.model._meta.object_name, num, kwargs))

    def count(self):
        self._evalQuery()
        return len(self._resultCache)

class LeafClassManager(models.Manager):
    def __init__(self, parentModel):
        super(LeafClassManager, self).__init__()
        self._parentModel = parentModel

    def contribute_to_class(self, model, name):
        if self._parentModel != None:
            self._parentModel._default_manager.registerChildClass(model)
        del self._parentModel
        super(LeafClassManager, self).contribute_to_class(model, name)

class AbstractClassManager(LeafClassManager):
    def __init__(self, parentModel):
        super(AbstractClassManager, self).__init__(parentModel)
        self._childClasses = []

    def get_query_set(self):
        return ChainQuerySet(self.model, self._childClasses)

    def registerChildClass(self, cls):
        self._childClasses.append(cls)
