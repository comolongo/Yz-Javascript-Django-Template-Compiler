#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)
from yz_js_django_tpl import BaseJsFilter, JsProcessorRegistry

class AddJsFilter(BaseJsFilter):
    """
    Converts the "add" filter in django templates to native javascript expression, 
    i.e. {{exampleVar|add:"2"}}
    Examples:
    >>> from yz_js_django_tpl import TemplateJsNode,JsTplSettings
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False
    >>> ###############
    >>> #test django "add" filter
    >>> ###############
    >>> js_tpl = TemplateJsNode('1 + 1 = {{ 1|add:"1" }}')
    >>> js_tpl.render()
    u'function(){return "1 + 1 = "+(1+1)}'
    >>> js_tpl = TemplateJsNode('{{ 1|add:"1" }}')
    >>> js_tpl.render()
    u'function(){return (1+1)}'
    """
    expected_filter_funcname = 'add'
    
    def render(self):
        return '(%s)' % '+'.join(self.js_func_params)

JsProcessorRegistry.register_js_filter(AddJsFilter)