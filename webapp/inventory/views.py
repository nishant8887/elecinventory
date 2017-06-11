# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import ComponentType, Property, Component
import json

def list_components(request):
    component_types = ComponentType.objects.all()
    return render(request, 'inventory/component_list.html', {'components': component_types})

def search_components(request, component_type_id):
    component_type = ComponentType.objects.get(id=component_type_id)
    properties = component_type.properties.all()
    return render(request, 'inventory/component_search.html', {'component_type': component_type, 'properties': properties})

def add_component(request, component_type_id):
    component_type = get_object_or_404(ComponentType, id=component_type_id)
    errors = []
    data = {}
    if request.method == "POST":
        req_data = json.loads(request.body)
        data, errors = process_component(component_type, req_data)
        if len(errors) == 0:
            c = Component()
            c.component_type = component_type
            c.quantity = data['quantity']
            c.box_id = data['box']
            del data['quantity']
            del data['box']
            c.component_data = data
            c.save()
            return HttpResponse(json.dumps({}), content_type="application/json")
        return HttpResponse({"errors": errors}, content_type="application/json", status=400)
    raise Http404

def get_property_values(request, component_type_id):
    if request.method == "GET":
        component_property = request.GET.get("property", None)
        if component_property is None:
            raise Http404

        property_values = []
        if component_property == 'box':
            property_values = Component.objects.filter(component_type__id=component_type_id).values_list('box_id', flat=True).distinct()
        else:
            component_value_str = "component_data -> '%s'" % component_property
            property_values = Component.objects.filter(component_type__id=component_type_id).extra(select=dict(v=component_value_str)).values_list('v', flat=True).distinct()

        property_values_list = []
        for v in property_values:
            if v is None or v.strip() == '':
                continue
            property_values_list.append(v)

        return HttpResponse(json.dumps({'property_values': property_values_list}), content_type="application/json")
    raise Http404

def search_items(request, component_type_id):
    if request.method == "POST":
        params = json.loads(request.body)
        page = int(params['page'])

        all_items = Component.objects.filter(component_type__id=component_type_id).order_by('id')
        paginator = Paginator(all_items, 2)

        total_pages = 0
        items = []

        properties = ComponentType.objects.get(id=component_type_id).properties.all()

        try:
            objs = paginator.page(page + 1)
            for obj in objs:
                v = {
                    'id': obj.id,
                    'box': obj.box_id,
                    'quantity': obj.quantity
                }
                s_text = ''
                for p in properties:
                    pv = obj.component_data.get(p.name, '-')

                    show_unit = False
                    if p.unit:
                        show_unit = True

                    if pv == '':
                        pv = '-'
                        show_unit = False

                    if show_unit:
                        s_text += '<tr><td>'+ p.name.title() + '</d><td>' + pv + ' ' + p.unit.title() + '</td></tr>'
                    else:
                        s_text += '<tr><td>'+ p.name.title() + '</td><td>' + pv + '</td></tr>'

                    v['text'] = s_text
 
                items.append(v)

            total_pages = paginator.num_pages
        except:
            page = 0
            total_pages = 0

        result = {
            'data': items,
            'page': page,
            'pages': total_pages
        }

        return HttpResponse(json.dumps(result), content_type="application/json")
    raise Http404

def update_component_quantity(request, component_id):
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

def update_component_box(request, component_id):
    if request.method == 'POST':
        box = request.POST.get('box', '')
        component = Component.objects.get(id=component_id)
        component.box_id = box
        component.save(update_fields=['box_id'])
        return HttpResponse(json.dumps({}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({}), content_type='application/json')

def process_component(component, parameters):
    data = {}
    errors = []
    for component_property in component.properties.all():
        property_value = parameters.get(component_property.name, None)
        if property_value is None or str(property_value).strip() == '':
            data[component_property.name] = ''
            continue

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

    print data
    return data, errors

# Create your views here.
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
            return HttpResponseRedirect('/inventory/%s/' % component_id)
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
