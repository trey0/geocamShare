
import datetime

from django import forms

from share2.shareCore.fields import UuidField

# the field names in this form are currently retained for backward compatibility with old versions
# of GeoCam Mobile
class UploadFileForm(forms.Form):
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
