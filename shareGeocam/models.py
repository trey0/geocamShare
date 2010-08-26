
from django.db import models

from share2.shareCore.models import Image
from share2.shareCore.managers import LeafClassManager

class Photo(Image):
    objects = LeafClassManager(parentModel=Image)
