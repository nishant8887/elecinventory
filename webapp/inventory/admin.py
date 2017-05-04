# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from inventory.models import Property, ComponentType, Component

# Register your models here.
class ComponentTypeAdmin(admin.ModelAdmin):
    filter_horizontal = ('properties',)

admin.site.register(Property)
admin.site.register(ComponentType, ComponentTypeAdmin)
admin.site.register(Component)