#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

from yz_js_django_tpl import BaseJsNode, JsProcessorRegistry, JsTplSettings

class ConstantIncludeJsNode(BaseJsNode):
    """
    Converts {% include %} tag in django into javascript expression
    
    Examples:
    >>> from yz_js_django_tpl import TemplateJsNode, JsTplSettings
    >>> from django.template import Template
    >>> ###############
    >>> #This object is pretty hard to test using doc test as we need an entire environment to setup
    >>> #hence for the time being we won't test it :(
    >>> ###############
    """
    expected_node_classname = 'ConstantIncludeNode'
    def _init_vars(self):
        tpl_path = self.django_node.template.name
        if tpl_path not in JsTplSettings.CONFIG['tpls']:
            raise NameError("Unabled to find template file %s in JsTplSettings.CONFIG[\'tpls\']" % tpl_path)
        tpl_info = JsTplSettings.CONFIG['tpls'][tpl_path]
        tpl_var_list = None
        self.tpl_func_name = tpl_info['tpl_func_name']
        if 'var_list' in tpl_info:
            tpl_var_list = tpl_info['var_list']
        self.tpl_var_list = tpl_var_list
        #add parameters of the include file into the global context of the calling file
        if tpl_var_list:
            [self.context.register_var(var_name, 'global') for var_name in tpl_var_list]
        self.update_parent_context()
    def generate_js_statement(self):
        return 'return %s' % self.generate_js_statement_as_closure()
    def generate_js_statement_as_closure(self):
        return self._wrap_expr_in_js_func(self.tpl_func_name, self.tpl_var_list)
JsProcessorRegistry.register_js_node(ConstantIncludeJsNode)