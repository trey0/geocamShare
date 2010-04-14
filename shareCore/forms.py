
import datetime

from django import forms

from share2.shareCore.fields import UuidField
from share2.shareCore.models import Track

# the field names in this form are currently retained for backward compatibility with old versions
# of GeoCam Mobile
class UploadImageForm(forms.Form):
    photo = forms.FileField(required=True)
    cameraTime = forms.DateTimeField(required=False)
    longitude = forms.FloatField(required=False)
    latitude = forms.FloatField(required=False)
    roll = forms.FloatField(required=False)
    pitch = forms.FloatField(required=False)
    yaw = forms.FloatField(required=False)
    tags = forms.CharField(max_length=256, required=False)
    notes = forms.CharField(max_length=2048, required=False)
    importFileMtimeUtc = forms.DateTimeField(required=False, initial=datetime.datetime.utcfromtimestamp(0))
    uuid = UuidField(required=False)

class UploadTrackForm(forms.ModelForm):
    trackUploadProtocolVersion = forms.CharField(initial='1.0', label='Track upload protocol version')
    gpxFile = forms.FileField(label='GPX file')
    referrer = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Track
        fields = ('name', 'owner', 'isAerial', 'icon', 'lineColor', 'lineStyle', 'tags', 'notes', 'uuid')
