# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import re
from django.forms import fields, widgets
from django.core.exceptions import ValidationError

class UuidField(fields.CharField):
    """Accepts an input UUID in the format you would get
    from str(uuid.uuid4())."""
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 128)
        super(UuidField, self).__init__(**kwargs)

    def clean(self, value):
        value = super(UuidField, self).clean(value)
        value = value.strip().lower()
        if value in fields.EMPTY_VALUES:
            return u''
        if re.search('^[0-9a-f\-]{36}$', value):
            return value
        else:
            raise ValidationError('Input string is not a valid UUID (should look like output of Python str(uuid.uuid4())).')
