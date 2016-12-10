from django.contrib import admin

from .models import Subject, class_group, House


admin.site.register(Subject)
admin.site.register(class_group)
admin.site.register(House)