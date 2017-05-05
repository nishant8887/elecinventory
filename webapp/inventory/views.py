# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
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
            quantity = int(quantity)
            if quantity < 0:
                errors.append('Non-negative value expected for quantity')
            data['quantity'] = quantity
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
            c.component_data = data
            c.save()
            return HttpResponseRedirect('/components/')
    return render(request, 'inventory/component.html', {'edit_type': False, 'name': component_type.name, 'properties': component_type.properties.all, 'errors': errors, 'data': data})

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
            component.component_data = data
            component.save()
            return HttpResponseRedirect('/components/%s/' % component_id)
    else:
        data = component.component_data
        data['quantity'] = component.quantity
        data['box'] = component.box_id

    return render(request, 'inventory/component.html', {'edit_type': True, 'name': component_type.name, 'properties': component_type.properties.all, 'errors': errors, 'data': data})

def view_component(request, component_id):
    component = Component.objects.get(id=component_id)
    component_type = component.component_type

    data = component.component_data
    data['quantity'] = component.quantity
    data['box'] = component.box_id

    return render(request, 'inventory/component_view.html', {'id': component.id, 'name': component_type.name, 'properties': component_type.properties.all, 'data': data})

def update_quantity_component(request, component_id):
    if request.method == 'POST':
        q = request.POST.get('diff', 0)
        try:
            q = int(q)
        except:
            return HttpResponseBadRequest()

        component = Component.objects.get(id=component_id)
        component.quantity += q

        if component.quantity < 0:
            return HttpResponseBadRequest()

        component.save(update_fields=['quantity'])
        return HttpResponse(json.dumps({}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({}), content_type='application/json')

def search_components(request):
    components = []
    data = []
    search_data = {}

    query = request.GET.get('q', '')
    if query != '':
        component_type = None
        ls = query.split('|')

        if len(ls) > 0:
            for l in ls:
                m = l.split(':')
                if len(m) == 2:
                    if m[0] == 'type':
                        component_type = m[1]
                    else:
                        search_data[m[0]] = m[1]

        data = search_data.keys()

        if component_type:
            components = Component.objects.filter(component_type__name=component_type, component_data__contains=search_data)
        else:
            components = Component.objects.filter(component_data__contains=search_data)

    return render(request, 'inventory/component_search.html', {'query': query, 'components': components, 'data': data})
