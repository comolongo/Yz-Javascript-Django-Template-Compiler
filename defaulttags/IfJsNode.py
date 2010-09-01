#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)
from yz_js_django_tpl import BaseJsNode, JsProcessorRegistry

class IfJsNode(BaseJsNode):
    """
    Converts if tag in django template into javascript expression
    Unit tests:
    >>> from yz_js_django_tpl import TemplateJsNode, JsTplSettings
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False
    >>> ###############
    >>> #test django IfNode object behaves as expected
    >>> ###############
    >>> from django.template import Template
    >>> django_tpl = Template('{% if cond > 5 %}true cond string{% else %}false cond string{% endif %}')
    >>> if_node = django_tpl.nodelist[0]
    >>> print if_node.var.first.text
    cond
    >>> print if_node.var.second.text
    5
    >>> print if_node.var.id
    >
    >>> print if_node.nodelist_true
    [<Text Node: 'true cond string'>]
    >>> print if_node.nodelist_false
    [<Text Node: 'false cond string'>]
    >>> ###############
    >>> #test if variable cond is larger than 5
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% if cond > 5 %}true cond string{% else %}false cond string{% endif %}')
    >>> js_tpl.render()
    u'function(cond){if(cond>5){return "true cond string"}else{return "false cond string"}}'
    >>> ###############
    >>> #test if variable cond is true or false
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% if cond %}true cond string{% else %}false cond string{% endif %}')
    >>> js_tpl.render()
    u'function(cond){if(cond){return "true cond string"}else{return "false cond string"}}'
    >>> ###############
    >>> #test if condition when comparing against string literal
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% if cond == "apple" %}true cond string{% else %}false cond string{% endif %}')
    >>> js_tpl.render()
    u'function(cond){if(cond=="apple"){return "true cond string"}else{return "false cond string"}}'
    >>> ###############
    >>> #test if condition with multiple subnodes
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% if cond %}true cond {{ var1 }} string{% else %}false cond string{% endif %}')
    >>> js_tpl.render()
    u'function(cond,var1){if(cond){return "true cond "+var1+" string"}else{return "false cond string"}}'
    >>> ###############
    >>> #test if condition with multiple subnodes in Versager mode
    >>> ###############
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = True
    >>> js_tpl = TemplateJsNode('{% if cond %}true cond {{ var1 }} string{% else %}false cond string{% endif %}')
    >>> js_tpl.render()
    u'function(cond,var1){if(cond){return ["true cond ",var1," string"].join("")}else{return "false cond string"}}'
    """
    expected_node_classname = 'IfNode'
    def _init_vars(self):
        if_condition_var = self.django_node.var
        if if_condition_var.id == 'literal':
            self.if_condition = self._extract_filter_expression(if_condition_var.value)
        else:
            self.if_condition = self._extract_filter_expression(if_condition_var.first.value) + \
                if_condition_var.id + self._extract_filter_expression(if_condition_var.second.value)
    def _init_sub_nodes(self):
        django_if_node = self.django_node
        self.if_block = self.scan_section(django_if_node.nodelist_true)
        self.else_block = None
        if django_if_node.nodelist_false:
            self.else_block = self.scan_section(django_if_node.nodelist_false)        
    def generate_js_statement(self):
        rendered_if_block = 'if(' + self.if_condition + '){' + self._nodes_to_js_str(self.if_block) + '}'
        rendered_else_block = ''
        if self.else_block:
            rendered_else_block = 'else{' + self._nodes_to_js_str(self.else_block) + '}'
        if_statement = rendered_if_block + rendered_else_block
        return if_statement
JsProcessorRegistry.register_js_node(IfJsNode)