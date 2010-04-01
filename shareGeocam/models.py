import os
import sys
import glob
import shutil

from PIL import Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.contrib.auth.models import User
from django.conf import settings

from share2.shareCore.utils import mkdirP, makeUuid

# so far no models needed in addition to shareCore models
