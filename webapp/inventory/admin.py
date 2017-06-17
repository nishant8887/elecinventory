# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from inventory.models import Property, ComponentType, Component, ComponentTypeProperties

# Register your models here.
class ComponentTypePropertiesInline(admin.TabularInline):
    model = ComponentTypeProperties
    extra = 1

class ComponentTypeAdmin(admin.ModelAdmin):
	inlines = (ComponentTypePropertiesInline,)

admin.site.register(Property)
admin.site.register(ComponentType, ComponentTypeAdmin)
admin.site.register(Component)