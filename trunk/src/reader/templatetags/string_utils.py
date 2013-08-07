from django import template
register = template.Library()
 
@register.filter()
def contains(value, arg):
    """
    Usage:
    {% if text|contains:"http://" %}
    This is a link.
    {% else %}
    Not a link.
    {% endif %}
    """
    
    if value is None:
        return False
    
    return arg in value

@register.filter()
def startswith(value, arg):
    """
    Usage:
    {% if text|startswith:"http://" %}
    This is a link.
    {% else %}
    Not a link.
    {% endif %}
    """
    
    if value is None:
        return False
    
    return value.startswith(arg)

@register.filter()
def endswith(value, arg):
    """
    Usage:
    {% if text|endswith:":8080" %}
    Has a port.
    {% else %}
    Doesn't have a port.
    {% endif %}
    """
    
    if value is None:
        return False
    
    return value.endswith(arg)

@register.filter()
def addspaceifnotempty(obj):
    """
    Usage:
    {{query|addspaceifnotempty}}
    """
    
    if obj is not None and not obj.endswith(" "):
        return obj + " "
    else:
        return obj
    
@register.filter()
def remove(value, arg):
    """
    Usage:
    {{text|remove:"remove this"}}
    """
    
    if value is not None:
        return value.replace(arg, "")
    else:
        return value