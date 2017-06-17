# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import ComponentType, Property, Component
import json


@login_required
def list_components(request):
    component_types = ComponentType.objects.all()
    return render(request, 'inventory/component_list.html', {'components': component_types})


@login_required
def search_components(request, component_type_id):
    component_type = ComponentType.objects.get(id=component_type_id)
    properties = component_type.properties.order_by('componenttypeproperties__order')
    return render(request, 'inventory/component_search.html', {'component_type': component_type, 'properties': properties})


@login_required
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
    return HttpResponse(status=405)


@login_required
def get_property_values(request, component_type_id):
    if request.method == "POST":
        data = json.loads(request.body)

        component_property = data['property']
        del data['property']

        if component_property is None:
            raise Http404

        search_data = {}
        for k in data:
            val = str(data[k]).strip()
            if val == '':
                continue
            if k != 'box':
                search_data[str(k)] = val

        if search_data.has_key(str(component_property)):
            del search_data[str(component_property)]

        search_items = Component.objects.filter(component_type__id=component_type_id, component_data__contains=search_data)

        property_values = []
        if component_property == 'box':
            property_values = search_items.values_list('box_id', flat=True).distinct()
        else:
            component_value_str = "component_data -> '%s'" % component_property
            property_values = search_items.extra(select=dict(v=component_value_str)).values_list('v', flat=True).distinct()

        property_values_list = []
        for v in property_values:
            if v is None or v.strip() == '':
                continue
            property_values_list.append(v)

        return HttpResponse(json.dumps({'property_values': property_values_list}), content_type="application/json")
    return HttpResponse(status=405)


@login_required
def search_items(request, component_type_id):
    if request.method == "POST":
        params = json.loads(request.body)
        page = int(params['page'])

        del params['page']

        search_box = None
        search_data = {}
        for k in params:
            val = str(params[k]).strip()
            if val == '':
                continue
            if k == 'box':
                search_box = val
            else:
                search_data[str(k)] = val

        search_items = Component.objects.filter(component_type__id=component_type_id)

        if search_box:
            search_items = search_items.filter(box_id=search_box)

        if len(search_data.keys()) > 0:
            search_items = search_items.filter(component_data__contains=search_data)

        search_items = search_items.order_by('id')

        paginator = Paginator(search_items, 10)

        total_pages = 0
        items = []

        properties = ComponentType.objects.get(id=component_type_id).properties.order_by('componenttypeproperties__order')

        try:
            objs = paginator.page(page + 1)
            for obj in objs:
                v = {
                    'id': obj.id,
                    'box': obj.box_id,
                    'quantity': obj.quantity
                }
                s_text = ''
                s_properties = []
                for p in properties:
                    pv = obj.component_data.get(p.name, None)

                    if pv is not None and pv != '':
                        if p.unit:
                            s_properties.append({'name': str(p.name), 'value': pv + ' ' + p.unit})
                        else:
                            s_properties.append({'name': str(p.name), 'value': pv})
                    else:
                        s_properties.append({'name': str(p.name), 'value': '-'})

                v['properties'] = s_properties

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
    return HttpResponse(status=405)


@login_required
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
    return HttpResponse(status=405)


@login_required
def update_component_box(request, component_id):
    if request.method == 'POST':
        box = request.POST.get('box', '')

        if box.trim() == '':
            return HttpResponse(status=400)

        component = Component.objects.get(id=component_id)
        component.box_id = box
        component.save(update_fields=['box_id'])
        return HttpResponse(json.dumps({}), content_type='application/json')
    return HttpResponse(status=405)


def process_component(component, parameters):
    data = {}
    errors = []
    for component_property in component.properties.order_by('componenttypeproperties__order'):
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

    return data, errors


def login_view(request):
    if request.method == 'GET':
        if request.user != AnonymousUser():
            return HttpResponseRedirect('/components/')
        return render(request, 'inventory/login.html', {})
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/components/')
        else:
            error = "Invalid username or password. Try again."
            return render(request, 'inventory/login.html', {'error': error, 'username': username})
    return HttpResponse(status=405)


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def edit_or_delete_component(request, component_id):
    component = Component.objects.get(id=component_id)
    component_type = component.component_type

    if request.method == "POST":
        # data, errors = process_component(component_type, request.POST)
        # if len(errors) == 0:
        #     component.quantity = data['quantity']
        #     component.box_id = data['box']
        #     del data['quantity']
        #     del data['box']
        #     component.component_data = data
        #     component.save()
        #     return HttpResponse(json.dumps({}), content_type="application/json")
        return HttpResponse(status=404)

    elif request.method == "DELETE":
        component.delete()
        return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(status=405)
