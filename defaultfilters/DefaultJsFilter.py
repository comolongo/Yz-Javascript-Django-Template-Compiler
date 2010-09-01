#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)
from yz_js_django_tpl import BaseJsFilter, JsProcessorRegistry

class DefaultJsFilter(BaseJsFilter):
    """
    Converts the "default" filter in django templates to javascript expression
    i.e. {{exampleVar|default:"default value"}}
    Examples:
    >>> from yz_js_django_tpl import TemplateJsNode,JsTplSettings
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False     
    >>> ###############
    >>> #test django "default" filter
    >>> ###############
    >>> js_tpl = TemplateJsNode('Default value text: {{testVar|default:"default val"}}')
    >>> js_tpl.render()
    u'function(testVar){return "Default value text: "+yzdjs_default(testVar,"default val")}'
    """
    expected_filter_funcname = 'default'
    js_func_name             = 'yzdjs_default'
    file_path                = __file__

JsProcessorRegistry.register_js_filter(DefaultJsFilter)