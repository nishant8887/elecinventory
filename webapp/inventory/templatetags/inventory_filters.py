from django import template

register = template.Library()

@register.filter
def get_value_from_dict(h, key):
    v = h.get(str(key), "")
    if v is None:
        v = ""
    return v
