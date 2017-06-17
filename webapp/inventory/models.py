# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import HStoreField

# Create your models here.
class Property(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'properties'

    def __unicode__(self):
        return '%s' % self.name

class ComponentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    properties = models.ManyToManyField(Property)

    def __unicode__(self):
        return '%s' % self.name

class Component(models.Model):
    component_type = models.ForeignKey(ComponentType)
    component_data = HStoreField()
    quantity = models.IntegerField(default=0)
    box_id = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s_%s' % (self.component_type.name, self.id)