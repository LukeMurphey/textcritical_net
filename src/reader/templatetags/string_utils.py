from django import template
register = template.Library()

def makestring(s):
    if isinstance(s, str):
        return s
    else:
        return str(s)

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
    
    return arg in makestring(value)

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
    
    return makestring(value).startswith(arg)

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
    
    return makestring(value).endswith(arg)

@register.filter()
def addspaceifnotempty(obj):
    """
    Usage:
    {{query|addspaceifnotempty}}
    """
    obj = makestring(obj)
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
        return makestring(value).replace(arg, "")
    else:
        return value
    
@register.filter()
def replace(value, arg):
    """
    Usage:
    {{text|replace:"replace_this,with_this"}}
    """
    
    split_s = arg.split(',', 1 )
    
    if len(split_s) >= 2:
        
        replace_this = split_s[0]
        put_in_this = split_s[1]
        return makestring(value).replace(replace_this, put_in_this)
    else:
        return value