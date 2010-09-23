#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)
from yz_js_django_tpl import BaseJsNode, JsProcessorRegistry

class AssignJsNode(BaseJsNode):
    """
    Converts assign tag in django template into javascript expression
    Unit tests:
    >>> from yz_js_django_tpl import TemplateJsNode, JsTplSettings
    >>> from yz_js_django_tpl.customtags import *
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False
    >>> ###############
    >>> #test django AssignNode object behaves as expected
    >>> ###############
    >>> from django.template import Template
    >>> django_tpl = Template('{%load assign%} example here: {% assign other_str "another"|capfirst %}')
    >>> assign_node = django_tpl.nodelist[2]
    >>> assign_node.name
    u'other_str'
    >>> assign_node.value.var
    u'another'
    >>> assign_node.value.filters[0][0].__name__
    'capfirst'
    >>> ###############
    >>> #test assign js node works
    >>> ###############
    >>> js_tpl = TemplateJsNode('{%load assign%} assigning here: {% assign other_str varA|add:"5" %} displaying here: {{ other_str }}')
    >>> js_tpl.render()
    u'function(varA){var other_str;return " assigning here: "+function(){other_str=(varA+5);return ""}()+" displaying here: "+other_str}'
    """
    expected_node_classname = 'AssignNode'
    def _init_vars(self):
        self.new_var_name       = self.context.register_var(self.django_node.name, scope="global", var_type="implicit")
        self.new_var_value_expr = self._extract_filter_expression(self.django_node.value)
    def generate_js_statement(self):
        #e.g. varA=123
        #e.g. function(){varA=123;return null}()
        return self.new_var_name + '=' + self.new_var_value_expr + ';return ""'
JsProcessorRegistry.register_js_node(AssignJsNode)