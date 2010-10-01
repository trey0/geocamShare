# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import datetime

from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User

from share2.shareCore.fields import UuidField
from share2.shareCore.models import Track, Image

# the field names in this form are currently retained for backward compatibility with old versions
# of GeoCam Mobile
class UploadImageForm(forms.Form):
    photo = forms.FileField(required=True)
    cameraTime = forms.CharField(required=False)
    longitude = forms.FloatField(required=False)
    latitude = forms.FloatField(required=False)
    roll = forms.FloatField(required=False)
    pitch = forms.FloatField(required=False)
    yaw = forms.FloatField(required=False)
    yawRef = forms.CharField(max_length=1, required=False)
    altitude = forms.FloatField(required=False)
    altitudeRef = forms.CharField(max_length=1, required=False)
    tags = forms.CharField(max_length=256, required=False)
    notes = forms.CharField(max_length=2048, required=False)
    importFileMtimeUtc = forms.DateTimeField(required=False, initial=datetime.datetime.utcfromtimestamp(0))
    uuid = UuidField(required=False)
    folder = forms.CharField(max_length=32, required=False)

class UploadTrackForm(forms.ModelForm):
    trackUploadProtocolVersion = forms.CharField(required=False, initial='1.0', label='Track upload protocol version')
    gpxFile = forms.FileField(label='GPX file')
    referrer = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Track
        fields = ('name', 'isAerial', 'icon', 'lineColor', 'lineStyle', 'tags', 'notes', 'uuid')

class EditImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditImageForm, self).__init__(*args, **kwargs)

        # change default widgets
        self.fields['notes'].widget = forms.TextInput(attrs={'size': '50'})
        self.fields['tags'].widget = forms.TextInput(attrs={'size': '50'})

    class Meta:
        model = Image
        fields = ('notes', 'tags', 'latitude', 'longitude', 'altitude', 'altitudeRef', 'yaw', 'yawRef', 'icon')

