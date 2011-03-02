# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.core.exceptions import ValidationError

from geocamShare.shareCore.utils import anyjson as json

class Extras(object):
    # At the moment this object exists pretty much solely to let you
    # get and set elements in its __dict__ dictionary via dotted
    # notation.  Someday it could do more.
    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    # This is here mostly so you can use the "in" keyword.
    def __iter__(self):
        return self.__dict__.__iter__()

class ExtrasField(models.TextField):
    '''A Django model field for storing extra schema-free data.  You can 
    get and set arbitrary properties on the extra field, which can be 
    comprised of strings, numbers, dictionaries, arrays, booleans, and 
    None.  These properties are stored in the database as a JSON-encoded 
    set of key-value pairs.'''

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargsin):
        kwargs = dict(blank=True)
        kwargs.update(**kwargsin)
        super(ExtrasField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value == '':
            return Extras()
        elif type(value) == Extras:
            return value
        else:
            extras = Extras()
            try:
                values = json.loads(value)
                assert type(values) == dict, 'expected a dictionary object, found a %s' % type(values).__name__
                for key in values.keys():
                    assert type(key) == unicode, 'expected unicode keys, found a %s' % type(key).__name__
                extras.__dict__ = values
            except (ValueError, AssertionError), e:
                raise ValidationError, 'Invalid JSON data in ExtrasField: %s' % e
            return extras

    def get_db_prep_value(self, value):
        return json.dumps(value.__dict__)
