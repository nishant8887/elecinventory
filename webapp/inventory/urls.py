from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^components/$', views.search_components),
    url(r'^components/add/$', views.list_components),
    url(r'^components/add/(?P<component_type_id>[0-9]+)/$', views.add_component),
    url(r'^components/(?P<component_id>[0-9]+)/edit/$', views.edit_component),
    url(r'^components/(?P<component_id>[0-9]+)/$', views.view_component),
    url(r'^components/(?P<component_id>[0-9]+)/update/$', views.update_quantity_component),
]