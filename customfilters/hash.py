#Access dictionary values with variable keys
#Code from: http://push.cx/2007/django-template-tag-for-dictionary-access and http://stackoverflow.com/questions/35948/django-templates-and-variable-attributes
from django.template import Library
register = Library()

@register.filter
def hash(h,key):
    if key in h:
        return h[key]
    else:
        return None