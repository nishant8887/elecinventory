from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^components/$', views.list_components),
    url(r'^components/(?P<component_type_id>[0-9]+)/$', views.search_components),
    url(r'^components/(?P<component_type_id>[0-9]+)/add/$', views.add_component),
    url(r'^components/(?P<component_type_id>[0-9]+)/property_values/$', views.get_property_values),
    url(r'^components/(?P<component_type_id>[0-9]+)/search/$', views.search_items),

    url(r'^inventory/(?P<component_id>[0-9]+)/$', views.view_component),
    url(r'^inventory/(?P<component_id>[0-9]+)/edit/$', views.edit_component),
    url(r'^inventory/(?P<component_id>[0-9]+)/update/$', views.update_component_quantity),
    url(r'^inventory/(?P<component_id>[0-9]+)/update/box/$', views.update_component_box),
]