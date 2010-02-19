
import os

from share2.shareCore.settings import *

CHECKOUT_DIR = os.environ['CHECKOUT_DIR']

DATA_DIR = os.path.join(CHECKOUT_DIR, 'data')
DATA_URL = os.path.join(os.environ['DJANGO_SCRIPT_NAME'], 'data')
