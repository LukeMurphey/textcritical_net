from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django import template
from django.utils import simplejson
register = template.Library()
 
@register.filter(is_safe=True)
def jsonify(obj):
    
    if isinstance(obj, QuerySet):
        return serialize('json', obj)
    
    return simplejson.dumps(object)
