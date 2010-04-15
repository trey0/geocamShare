
import datetime

from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User

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
    ownerName = forms.CharField(max_length=40, required=True)
    trackUploadProtocolVersion = forms.CharField(initial='1.0', label='Track upload protocol version')
    gpxFile = forms.FileField(label='GPX file')
    referrer = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Track
        fields = ('name', 'ownerName', 'isAerial', 'icon', 'lineColor', 'lineStyle', 'tags', 'notes', 'uuid')

    def clean(self):
        super(UploadTrackForm, self).clean()
        # better to define a new field type and do validation there
        if self.cleaned_data.has_key('ownerName'):
            try:
                owner = User.objects.get(username=self.cleaned_data['ownerName'])
            except:
                raise ValidationError('Invalid ownerName %s' % self.cleaned_data['ownerName'])
            else:
                self.cleaned_data['owner'] = owner
        return self.cleaned_data
