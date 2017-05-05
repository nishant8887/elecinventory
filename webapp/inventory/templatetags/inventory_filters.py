from django import template

register = template.Library()

@register.filter
def get_value_from_dict(h, key):
    v = h.get(str(key), "")
    if v is None:
        v = ""
    return v

@register.filter
def get_value_from_dict_for_show(h, key):
    v = h.get(str(key), "--")
    if v is None:
        v = "--"
    return v