# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ComponentType, Property, Component
import json

def process_component(component, parameters):
    data = {}
    errors = []
    for component_property in component.properties.all():
        property_value = parameters.get(component_property.name, None)
        if property_value is None or str(property_value).strip() == '':
            errors.append('Empty value for %s' % component_property.name)
            property_value = ''

        property_value = str(property_value)
        property_key = str(component_property.name)

        if property_value != '' and (component_property.unit is not None and component_property.unit.strip() != ''):
            try:
                float(property_value)
            except:
                errors.append('Non-numeric value for %s' % property_key)

        data[property_key] = property_value

    quantity = parameters.get('quantity', None)
    if quantity is None or str(quantity).strip() == '':
        errors.append('Empty value for quantity')
        data['quantity'] = ''
    else:
        try:
            data['quantity'] = float(quantity)
        except:
            data['quantity'] = quantity
            errors.append('Non-numeric value for quantity')

    box = parameters.get('box', None)
    if box is None or str(box).strip() == '':
        errors.append('Empty value for box')
        data['box'] = ''
    else:
        data['box'] = box

    return data, errors

# Create your views here.
def list_components(request):
    component_types = ComponentType.objects.all()
    return render(request, 'inventory/component_list.html', {'components': component_types})

def add_component(request, component_type_id):
    component_type = ComponentType.objects.get(id=component_type_id)
    errors = []
    data = {}
    if request.method == "POST":
        data, errors = process_component(component_type, request.POST)
        if len(errors) == 0:
            c = Component()
            c.component_type = component_type
            c.quantity = data['quantity']
            c.box_id = data['box']
            del data['quantity']
            del data['box']
            c.component_data = json.dumps(data)
            c.save()
            return HttpResponseRedirect('/')
    return render(request, 'inventory/component.html', {'name': component_type.name, 'properties': component_type.properties.all, 'errors': errors, 'data': data})

def edit_component(request, component_id):
    component = Component.objects.get(id=component_id)
    component_type = component.component_type
    errors = []

    if request.method == "POST":
        data, errors = process_component(component_type, request.POST)
        if len(errors) == 0:
            component.quantity = data['quantity']
            component.box_id = data['box']
            del data['quantity']
            del data['box']
            component.component_data = json.dumps(data)
            component.save()
            return HttpResponseRedirect('/')
    else:
        data = json.loads(component.component_data)
        data['quantity'] = component.quantity
        data['box'] = component.box_id

    return render(request, 'inventory/component.html', {'name': component_type.name, 'properties': component_type.properties.all, 'errors': errors, 'data': data})
