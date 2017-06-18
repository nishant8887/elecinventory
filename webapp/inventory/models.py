# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import HStoreField


class Property(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'properties'

    def __unicode__(self):
        return '%s' % self.name


class ComponentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    properties = models.ManyToManyField(Property, through='ComponentTypeProperties')

    def __unicode__(self):
        return '%s' % self.name


class Component(models.Model):
    component_type = models.ForeignKey(ComponentType)
    component_data = HStoreField()
    quantity = models.IntegerField(default=0)
    box_id = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s_%s' % (self.component_type.name, self.id)

    def validate_unique(self, exclude=None):
        super(Component, self).validate_unique(exclude)
        existing = self.__class__.objects.filter(component_type=self.component_type, component_data__contains=self.component_data)
        if self.pk is None:
            if len(existing) != 0:
                raise ValidationError('Component already exists.')
        else:
            if len(existing) > 0 and existing[0].id != self.id:
                raise ValidationError('Component already exists.')

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Component, self).save(*args, **kwargs)


class ComponentTypeProperties(models.Model):
    component_type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    order = models.IntegerField()
