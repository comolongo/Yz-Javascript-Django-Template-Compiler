#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

from django.template import Template
import django.template
from django.template.loader import get_template
from django.utils.html import strip_spaces_between_tags
import os
import re
remove_whitespaces = re.compile(r'\s+')

class JsTplSettings(object):
    filters_in_use = {}
    CONFIG = {
        'VERSAGER_MODE' : False, #i.e. loser mode i.e. IE6
        'generated_js_file_location': None,
        'js_dependencies_location'  : None,
        'tpls' : {}
    }
    @classmethod
    def init_config(cls, config_dict):
        filters_in_use = {}
        cls.CONFIG = config_dict.copy()
def generate_js_tpl_file():
    """
    generates a javascript file with django templates as javascript functions
    file_location - path of where the generated file will be put
    tpl_info_list - dictionary of each django template to be converted to javascript. Look into the
    demo folder to see the format of the tpl_info_list
    """
    file_location = JsTplSettings.CONFIG['generated_js_file_location']
    js_tpl_file_contents = []
    tpl_info_list = JsTplSettings.CONFIG['tpls']
    print "opening " + file_location + " to generate javascript template file"
    js_tpl_file = open(file_location,"w+")
    js_tpl_file_contents = ["//Auto generated JS file for via yz_js_django_tpl\n"]    
    for tpl_path in tpl_info_list:
        tpl_info = tpl_info_list[tpl_path]
        tpl_var_list = None
        if 'var_list' in tpl_info:
            tpl_var_list = tpl_info['var_list']
        tpl_func_name = tpl_info['tpl_func_name']
        tpl_node = TemplateJsNode(django_template_path = tpl_path, var_list = tpl_var_list)
        js_tpl_file_contents.append('var ' + tpl_func_name + '=' + tpl_node.render())
        if len(js_tpl_file_contents) > 50:
            print "writing javascript expression batch to file"
            #ensures that we write to disk and clear the memory after every so many files so we don't
            #run out of ram
            js_tpl_file.writelines("\n".join(js_tpl_file_contents))
            js_tpl_file_contents = []
            js_tpl_file.close()
            js_tpl_file = open(file_location,"a")
    js_tpl_file.write("\n".join(js_tpl_file_contents))
    js_tpl_file.close()
    print "yz_js_django_tpl::generate_js_tpl_file successfully finished generating javascript template file"
    if JsTplSettings.CONFIG['js_dependencies_location']:
        filters_in_use = JsTplSettings.filters_in_use
        print "Checking to see if any javascript include files need to be added"
        if not filters_in_use:
            print "No function definitions need to be included"
        else:
            js_include_file = open(JsTplSettings.CONFIG['js_dependencies_location'],"w+")
            file_contents = ["//DO NOT EDIT! Your changes may be wiped as this is an auto generated JS file via yz_js_django_tpl\n"]
            file_contents.append("//This file contains function definitions that will be used in the javascript template files.")
            file_contents.append("//Most of javascript functions defined here are for filter functionality")
            js_include_file.write("\n".join(file_contents) + "\n")
            js_include_file.close()
            js_include_file = open(JsTplSettings.CONFIG['js_dependencies_location'],"a+")
            for filter_classname in filters_in_use:
                filter_info = filters_in_use[filter_classname]
                js_file_path = filter_info['js_file_path']
                if not js_file_path:
                    continue
                js_func_file = open(js_file_path, 'r')
                js_include_file.write("\n" + js_func_file.read())
                js_func_file.close()
            js_include_file.close()
                
class JsProcessorRegistry(object):
    """
    Keeps track of the js nodes and filters available and decides on which one to use 
    given a specified django node or filter
    """
    django_to_js_nodes = {}
    django_to_js_filters = {}

    @classmethod
    def register_js_node(cls, js_node_class):
        django_node_classnames = js_node_class.expected_node_classname
        if django_node_classnames.__class__.__name__ == 'str':
            django_node_classnames = [django_node_classnames]
        for django_node_classname in django_node_classnames:
            cls.django_to_js_nodes[django_node_classname] = js_node_class
        return js_node_class
    
    @classmethod
    def register_js_filter(cls, js_filter_class):
        django_filter_funcname = js_filter_class.expected_filter_funcname
        if js_filter_class.file_path and js_filter_class.js_func_name:
            js_file_path = os.path.dirname(js_filter_class.file_path) + '/' + js_filter_class.__name__ + '.js'
            js_filter_class.js_file_path = js_file_path
        cls.django_to_js_filters[django_filter_funcname] = js_filter_class
        return js_filter_class

    @classmethod
    def get_js_node(cls, django_node_classname):
        if django_node_classname in cls.django_to_js_nodes:
            return cls.django_to_js_nodes[django_node_classname]
        else :
            None

    @classmethod
    def get_js_filter(cls, django_filter_funcname):
        if django_filter_funcname in cls.django_to_js_filters:
            js_filter_class = cls.django_to_js_filters[django_filter_funcname]
            js_filter_classname = js_filter_class.__class__.__name__
            if js_filter_classname not in JsTplSettings.filters_in_use:
                JsTplSettings.filters_in_use[js_filter_classname] = {
                    'js_file_path': js_filter_class.js_file_path
                }
            return js_filter_class
        else :
            None
    

class JsNodeContext():
    """
    Keeps track of the variables accessable to a specific js node or filter
    Whenever a node or filter parses a variable into javascript, it either registers it with the context
    or gets it from the context. Either way, all variables that are rendered into javascript go through
    this method.
    """
    _var_generator_cntr = 0
    _global_cross_context_var_list = {}
    def __init__(self):
        self.global_vars = {} #vars global to the current context scope
        self.local_vars = {} #vars local to the current context scope
        self.vars_used_in_parent = {} #keeps track of all the variables used in a parent node
        self.vars_in_use = {} #keeps track of all the variables used in the current node
        self.vars_used_in_children = {} #keeps track of all variables used in child nodes
        self.rename_vars = {} #dictionary to rename variable in register_var()

    @classmethod
    def reset_global_context(cls):
        cls._var_generator_cntr = 0
        cls._global_cross_context_var_list = {}
    def register_var(self, base_var_name, scope, from_parent_or_child = None, full_var_name = None, var_type='input'):
        """
        Registers a variable so it can be rendered into javascript. This ensures that variables global to a given
        closure context in javascript are pass correctly from its parent js node and that each closure is only passed
        the variables that it needs. It also allows for a node to know which variables have been called in its
        parents and child nodes, which could be useful for nodes such as the ForJsNode, which depending on whether or not
        certain variables are called (e.g. forloop.counter), it will choose whether or not to define certain variables
        
        var_type - can be either input or implicit . input variables will we passed in via its calling functions via the
        input parameters, implicit variables will not be passed via the input parameters but will be assumed to be part
        of the global scope
        """
        if scope == 'local':
            var_list = self.local_vars
        elif scope == 'global':
            var_list = self.global_vars
        else:
            raise NameError('scope not defined')

        #full variable name example a.b
        #base variable name example a
        if not full_var_name:
            full_var_name = base_var_name
        if full_var_name in self.rename_vars:
            full_var_name = self.rename_vars[full_var_name]
            base_var_name = full_var_name
        else:
            self.__class__._global_cross_context_var_list[base_var_name] = var_type
        var_list[base_var_name] = var_type
        if from_parent_or_child == 'parent':
            var_usage_list = self.vars_used_in_parent
        elif from_parent_or_child == 'child':
            var_usage_list = self.vars_used_in_children
        else:
            var_usage_list = self.vars_in_use
        var_usage_list[full_var_name] = var_type
        return full_var_name

    def merge_js_vars(self, new_js_vars, scope):
        for var_name, var_type in new_js_vars.items():
            if var_name not in self.local_vars and \
                var_name not in self.global_vars:
                self.register_var(var_name, scope, var_type=var_type)

    def get_js_var_type(self, js_var_name):
        if js_var_name in self.local_vars:
            return self.local_vars[js_var_name]
        elif js_var_name in self.global_vars:
            return self.global_vars[js_var_name]
        else:
            raise NameError('variable does not exist')

    def get_vars_of_type(self, var_type):
        var_names = []
        for js_var_name in self.global_vars:
            if self.global_vars[js_var_name] == var_type:
                var_names.append(js_var_name)

        return var_names

    def create_new_var(self, scope, var_type='input'):
        """creates and registers a new variable name to use in javascript"""
        is_taken = True
        cntr = self.__class__._var_generator_cntr
        if (scope != 'local') and (scope != 'global'):
            raise NameError('scope not defined')

        while (is_taken == True):
            new_var_name = 'n' + str(cntr)
            if new_var_name in self.__class__._global_cross_context_var_list:
                is_taken = True
            else:
                self.register_var(new_var_name, scope, var_type)
                is_taken = False
            cntr += 1
        return new_var_name

class BaseJsTpl(object):
    """
    Base object for converting django template nodes/filters into javascript representation
    """
    def __init__(self, parent_js_node):
        self.context = JsNodeContext()
        self.parent_js_node = parent_js_node
        if parent_js_node:
            self.context.rename_vars.update(parent_js_node.context.rename_vars)
    def register_var_obj(self, var_obj):
        """Given a django Variable object, returns the variable name and registers it into context"""
        #if our variable was a property, e.g. a.b, base varname would be 'a'
        full_var_name = var_obj.var
        if var_obj.lookups:#if var_obj represents a literal i.e. 'apple', 5, etc., then we don't do anything
            base_varname = var_obj.lookups[0]
            full_var_name = self.context.register_var(base_varname, scope="global", full_var_name = full_var_name)
        return full_var_name
    def _wrap_expr_in_js_anon_func(self, js_expr, execute_now = True, var_list = None, show_params=False):
        """
        given a javascript expression, wraps it into a closure, e.g. function(if_cond){if(if_cond){return a}}(if_cond,a)
        """
        input_vars_list = self.context.get_vars_of_type('input')
        if var_list:
            unaccounted_vars = set(input_vars_list).symmetric_difference(set(var_list))
            if len(unaccounted_vars):
                msg = 'Input variables and given variables do not match. \n \
                    input vars: %s \n \
                    given vars: %s' % (','.join(input_vars_list), ','.join(var_list))
                
                raise NameError(msg)
            input_vars_list = var_list
        func_params = ''
        if show_params:
            func_params = ','.join(input_vars_list)
        if execute_now:
            func_execution = '(' + func_params + ')'
        else:
            func_execution = ''
        return 'function(' + func_params + '){' + js_expr + '}' + func_execution
    def _wrap_expr_in_js_func(self, func_name, func_params):
        """calls a javascript function, e.g. yzdjs_default(val, defaultVal)"""
        return func_name + '(' + ','.join(func_params) + ')'
    def _list_to_js_str(self, python_list):
        """converts a python list into a javascript string"""
        if JsTplSettings.CONFIG['VERSAGER_MODE']: 
            #old browsers like IE6 don't like string concatenation, hence we do join
            return '[' + ','.join(map(str, python_list)) + '].join("")'
        else:
            #newer browsers are optimized to do string concatenation and it is actually faster
            #than creating an array and doing join
            return '+'.join(map(str, python_list))
    def update_parent_context(self, parent_same_closure = False):
        """
        Makes sure that the variables global to the child are also being accounted for by
        the parent node. If the parent node did not define the variable locally, then it will 
        be assumed to be global to the parent node
        """
        if self.parent_js_node:
            parent_context = self.parent_js_node.context
            parent_context.merge_js_vars(self.context.global_vars, 'global')
            parent_context.vars_used_in_children.update(self.context.vars_in_use)
            parent_context.vars_used_in_children.update(self.context.vars_used_in_children)
            if parent_same_closure:
                parent_context.merge_js_vars(self.context.local_vars, 'local')
            
    def generate_js_statement(self):
        return None
    def generate_js_statement_as_closure(self):
        return None
    def render(self, as_closure = False):
        if (as_closure) :
            js_stmt = self.generate_js_statement_as_closure()
        else:
            js_stmt = self.generate_js_statement()
        self.update_parent_context()
        return js_stmt

class BaseJsFilter(BaseJsTpl):
    """
    Base filter for converting django filters into javascript expressions
    """
    file_path = None
    js_file_path = None
    js_func_name = None #name of javascript function to call in order to process the given filter value and arguments 
    def __init__(self, parent_js_node, expr, arg_info):
        super(BaseJsFilter, self).__init__(parent_js_node)
        self.parent_js_node
        self.expr = expr
        self.js_func_params = [expr]
        arg = None
        if (len(arg_info) == 2):
            arg_is_var, arg = arg_info      
            if arg_is_var: #checks if argument is a django Variable object, if so register it
                arg = self.register_var_obj(arg)
                self.update_parent_context();
            else:
                #check if arg is a number
                try:
                    float(arg)
                except ValueError:
                    arg  = '"' + arg + '"'
        self.arg = arg
        if arg:
            self.js_func_params.append(arg)
    def generate_js_statement(self):
        """
        renders the javascript expression for processing the filter
        just like the django filters, the javascript filters should follow the conventions of filtername(var, argument)
        """
        return self._wrap_expr_in_js_func(self.__class__.js_func_name, self.js_func_params)
    def generate_js_statement_as_closure(self):
        return self.generate_js_statement()
        
class BaseJsNode(BaseJsTpl):
    def __init__(self, django_node = None, parent_js_node = None):
        super(BaseJsNode, self).__init__(parent_js_node)
        self.django_node = django_node
        self._init_vars()
        self._init_sub_nodes()
        if parent_js_node:
            self.update_parent_context()
    def _init_vars(self):
        """
        Registers and declares local and global variables used by current node
        """
        return None
    def _init_sub_nodes(self):
        """
        use scan_section to initialize any subnodes of the current node
        """
        return None
    def scan_section(self, django_tpl_nodelist):
        """
        loops through list of django nodes - usually child nodes - and converts them into list of initialized js nodes
        """
        js_nodes = []
        for django_tpl_node in django_tpl_nodelist:
            js_node = JsProcessorRegistry.get_js_node(django_tpl_node.__class__.__name__)
            if js_node:
                js_nodes.append(js_node(django_tpl_node, self))
        return js_nodes

    def _extract_filter_expression(self, django_filter_expression):
        """
        given a django FilterExpression object, register the containing variables and 
        initialize any of the filters defined by the FilterExpression
        e.g. {{varName|add:"5"|default:10}} -> yzdjs_default(yzdjs_add(varName, 5), 10)
        """
        var_obj = django_filter_expression.var
        filters = django_filter_expression.filters
        if isinstance(var_obj, django.template.Variable):
            var_expr = self.register_var_obj(var_obj)
        else:
            var_expr = '"%s"' % var_obj
        if filters:
            for django_filter, filter_args in filters:
                js_filter_class = JsProcessorRegistry.get_js_filter(django_filter.__name__)
                if js_filter_class:
                    js_filter = js_filter_class(self, var_expr, filter_args[0])
                    var_expr = js_filter.render()
        return var_expr

    def _nodes_to_js_str(self, nodes_list, as_closure = False):
        """converts a list of nodes, generally child nodes to a javascript expression"""
        #optimization to check if there is only one node, if so then we could potentially forgo the declaration of a 
        #closure and improve performance a little bit
        #e.g. instead of function(cond, another_cond){if(cond){return [function(another_cond){if(another_cond){return 'test string'}}(another_cond)].join("")}}(cond, another_cond)
        #we could save a join() and anonymous function call as well as a few characters by doing:
        #function(cond, another_cond){if(cond){if(another_cond){return 'test string'}}(cond, another_cond)
        if len(nodes_list) == 1:
            if as_closure:
                rendered_nodes = nodes_list[0].render(as_closure = True)
            else:
                rendered_nodes = nodes_list[0].render()
        else:
            if as_closure:
                rendered_nodes = self._list_to_js_str(nodes_list)
            else:
                rendered_nodes = 'return ' + self._list_to_js_str(nodes_list)
        #updates the parent context so it knows of what variables its child is using
        self.update_parent_context(parent_same_closure = not as_closure)
        return rendered_nodes
    def __str__(self):
        return self.render(as_closure = True)
    def generate_js_statement_as_closure(self):
        return self._wrap_expr_in_js_anon_func(js_expr = self.generate_js_statement())

class TemplateJsNode(BaseJsNode):
    """Main node that represents a document and contains all subnodes"""
    def __init__(self, django_template_string = None, django_template_path = None, var_list = None):
        self.var_list = var_list
        if django_template_string:
            django_tpl_node = Template(django_template_string)
        elif django_template_path:
            django_tpl_node = get_template(django_template_path)
        else:
            raise NameError('neither django_template_string nor django_template_path is defined, at least one needs to be set')
        JsNodeContext.reset_global_context()
        super(TemplateJsNode, self).__init__(None)
        self.js_nodes = self.scan_section(django_tpl_node.nodelist)

    def generate_js_statement(self):
        js_expr       = ''
        implicit_vars = self.context.get_vars_of_type('implicit')
        if len(implicit_vars):
            js_expr += 'var ' + ','.join(implicit_vars) + ';'
        js_expr += self._nodes_to_js_str(self.js_nodes)
        rendered_content = self._wrap_expr_in_js_anon_func(js_expr = js_expr, execute_now = False, var_list = self.var_list, show_params = True)   
        rendered_content = strip_spaces_between_tags(rendered_content)
        return remove_whitespaces.sub(' ', rendered_content.strip())

    def generate_js_statement_as_closure(self):
        return self.render()

class VariableJsNode(BaseJsNode):
    """
    processes and renders a django variable tag i.e. {{ variable_name }} or 
    {{ variable_name|filter1|filter2... }}

    Examples:
    >>> ###############
    >>> #test django VariableNode behaves as expected
    >>> ###############
    >>> from django.template import Template
    >>> django_tpl = Template('{{ var }}')
    >>> django_tpl.nodelist[0].filter_expression.__dict__
    {'var': <Variable: u'var'>, 'token': u'var', 'filters': []}
    >>> django_tpl = Template('{{ var.subvar }}')
    >>> django_tpl.nodelist[0].filter_expression.__dict__
    {'var': <Variable: u'var.subvar'>, 'token': u'var.subvar', 'filters': []}
    >>> django_tpl.nodelist[0].filter_expression.var.__dict__
    {'var': u'var.subvar', 'literal': None, 'translate': False, 'lookups': (u'var', u'subvar')}
    >>> ###############
    >>> #test VariableJsNode
    >>> ###############
    >>> js_tpl = TemplateJsNode('{{ var }}')
    >>> js_tpl.render()
    u'function(var){return var}'
    >>> js_tpl = TemplateJsNode('{{ var.subvar }}')
    >>> js_tpl.render()
    u'function(var){return var.subvar}'
    """
    expected_node_classname = ['VariableNode', 'DebugVariableNode']
    def _init_vars(self):
        django_filter_expression = self.django_node.filter_expression
        self.var_expr = self._extract_filter_expression(django_filter_expression)
        self.update_parent_context()
    def generate_js_statement(self):
        return 'return ' + self.var_expr
    def generate_js_statement_as_closure(self):
        return self.var_expr
JsProcessorRegistry.register_js_node(VariableJsNode)

class TextJsNode(BaseJsNode):
    """
    Converts django's TextNode to javascript expression. This node handles the strings between the tags and filters
    Examples:
    >>> ###############
    >>> #test django TextNode behaves as expected
    >>> ###############
    >>> from django.template import Template
    >>> django_tpl = Template('text string')
    >>> django_tpl.nodelist[0].__dict__
    {'source': (<django.template.StringOrigin object at 0x102805750>, (0, 11)), 's': u'text string'}
    >>> django_tpl.nodelist[0].s
    u'text string'
    >>> ###############
    >>> #test TextJsNode
    >>> ###############
    >>> js_tpl = TemplateJsNode('text string')
    >>> js_tpl.render()
    u'function(){return "text string"}'
    """
    expected_node_classname = 'TextNode'
    def _init_vars(self):
        self.text = self.django_node.s
    def generate_js_statement(self):
        return 'return ' + self.generate_js_statement_as_closure()
    def generate_js_statement_as_closure(self):
        return '"' + self.text.replace('"', '\\"') + '"'
JsProcessorRegistry.register_js_node(TextJsNode)

#loads all of the filters in the defaulttags and defaultfilters folders, this makes it easy to drop in new tags and filters
#as they are being created
from yz_js_django_tpl.defaulttags import *
from yz_js_django_tpl.defaultfilters import *