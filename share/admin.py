
from django.contrib import admin

from share2.share.models import ALL_TASKS_DICT

for taskType in ALL_TASKS_DICT.values():
    admin.site.register(taskType)
