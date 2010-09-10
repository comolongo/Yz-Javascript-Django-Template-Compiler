#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)
from yz_js_django_tpl import BaseJsFilter, JsProcessorRegistry

class HashJsFilter(BaseJsFilter):
    """
    Converts the "hash" filter in django templates to native javascript hash look up, 
    i.e. {{exampleVar|hash:varB}}
    Examples:
    >>> from yz_js_django_tpl import TemplateJsNode,JsTplSettings
    >>> from yz_js_django_tpl.customfilters import *
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False
    >>> ###############
    >>> #test django "hash" filter
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% load hash %}Dict var1 with hash varB{{ varA|hash:varB }}')
    >>> js_tpl.render()
    u'function(varA,varB){return "Dict var1 with hash varB"+varA[varB]}'
    """
    expected_filter_funcname = 'hash'
    
    def render(self):
        return '%s[%s]' % (self.expr, self.arg)

JsProcessorRegistry.register_js_filter(HashJsFilter)