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
    
    return value.endswith(arg)