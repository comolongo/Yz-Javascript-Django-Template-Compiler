#Useful template plugin for assigning new variables. Code taken from http://djangosnippets.org/snippets/539/
from django import template
register = template.Library()
class AssignNode(template.Node):
    """
    Sometimes you want to create a temporal variable to store something or do anything you want with it, problem is that django template system doesn't provide this kind of feature. This template tag is just for that.

    Syntax::

        {% assign [name] [value] %}

    This will create a context variable named [name] with a value of [value] [name] can be any identifier and [value] can be anything. If [value] is a callable, it will be called first and the returning result will be assigned to [name]. [value] can even be filtered.

    Example::

    {% assign count 0 %} {% assign str "an string" %} {% assign number 10 %} {% assign list entry.get_related %} {% assign other_str "another"|capfirst %}

    {% ifequal count 0 %} ... {% endifequal %}

    {% ifequal str "an string" %} ... {% endifequal %}

    {% if list %} {% for item in list %} ... {% endfor %} {% endif %}

    Author:
        jmrbcu
    Posted:
        January 9, 2008    
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''

def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.
    
    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}
        
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)

register.tag('assign', do_assign)