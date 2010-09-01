#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

from yz_js_django_tpl import BaseJsNode, JsProcessorRegistry, JsTplSettings

class ForJsNode(BaseJsNode):
    """
    converts django ForNode to javascript expression
    This objects listens to which forloop helper variables (i.e. forloop.counter, forloop.first, etc) are
    being called in the child subnodes and instantiates them only necessary. So if a child node
    uses forloop.first, then we instantiate that variable here, otherwise, we don't, and there by save
    a few characters of code and a few cycles of cpu.
    The forloop.counter0 is basically the loop iterator, hence it is just renamed to the 
    variable name of the for iterator.

    Examples:
    >>> from yz_js_django_tpl import TemplateJsNode, JsTplSettings
    >>> ###############
    >>> #test django ForNode object behaves as expected
    >>> ###############
    >>> from django.template import Template
    >>> django_tpl = Template('{% for arr_ele in arr %}<h1>for loop text</h1>{% endfor %}')
    >>> for_node = django_tpl.nodelist[0]
    >>> print for_node.loopvars
    [u'arr_ele']
    >>> print for_node.sequence
    arr
    >>> print for_node.nodelist_loop
    [<Text Node: '<h1>for loop text</h1>'>]
    >>> print for_node.is_reversed
    False
    >>> print for_node.nodelist_empty
    []
    >>> ###############
    >>> #test basic for loop
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}<h1>for loop text</h1>{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){for(var n0=0,arr_ele,n2=arr.length,n1="";n0<n2;n0++){arr_ele=arr[n0];n1+="<h1>for loop text</h1>"} return n1}'
    >>> ###############
    >>> #test for empty array
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}<h1>for loop text</h1>{% empty %}Lo siento empty array{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){var n2=arr.length;if(n2){for(var n0=0,arr_ele,n1="";n0<n2;n0++){arr_ele=arr[n0];n1+="<h1>for loop text</h1>"} return n1}else{return "Lo siento empty array"}}'
    >>> ###############
    >>> #test for empty array in Versager Mode
    >>> ###############
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = True
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}<h1>for loop text</h1>{% empty %}Lo siento empty array{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){var n2=arr.length;if(n2){for(var n0=0,arr_ele,n1=[];n0<n2;n0++){arr_ele=arr[n0];n1[n1.length]="<h1>for loop text</h1>"} return n1.join("")}else{return "Lo siento empty array"}}'
    >>> ###############
    >>> #test for loop iterator variables i.e. forloop.counter, forloop.counter0
    >>> ###############
    >>> JsTplSettings.CONFIG['VERSAGER_MODE'] = False
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}iterator value: {{forloop.counter0}} iterator plus one: {{forloop.counter}}{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){for(var n0=0,arr_ele,n4,n2=arr.length,n1="";n0<n2;n0++){arr_ele=arr[n0],n4=n0+1;n1+="iterator value: "+n0+" iterator plus one: "+n4} return n1}'
    >>> ###############
    >>> #test for loop reverse iterator variables i.e. forloop.revcounter, forloop.revcounter0
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}forloop.revcounter0 : {{forloop.revcounter0}} forloop.revcounter: {{forloop.revcounter}}{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){for(var n0=0,arr_ele,n5,n6,n2=arr.length,n1="";n0<n2;n0++){arr_ele=arr[n0],n5=n2-n0-1,n6=n2-n0;n1+="forloop.revcounter0 : "+n6+" forloop.revcounter: "+n5} return n1}'
    >>> ###############
    >>> #test for loop iterator variables forloop.first, forloop.last
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}forloop.first : {{forloop.first}} forloop.last: {{forloop.last}}{% endfor %}')
    >>> js_tpl.render()
    u'function(arr){for(var n0=0,arr_ele,n8,n7,n2=arr.length,n3=n2-1,n1="";n0<n2;n0++){arr_ele=arr[n0],n8=(n0==n3),n7=(n0==0);n1+="forloop.first : "+n7+" forloop.last: "+n8} return n1}'
    >>> ###############
    >>> #test for loop parent iterator variables
    >>> ###############
    >>> js_tpl = TemplateJsNode('{% for arr_ele in arr %}{% for ele2 in arr2 %}inner loop iterator: {{ forloop.counter }} parent loop iterator: {{ forloop.parentloop.counter }}{% endfor %}{% endfor %}')
    >>> js_tpl.render()
    u'function(arr,arr2){for(var n0=0,arr_ele,n4,n2=arr.length,n1="";n0<n2;n0++){arr_ele=arr[n0],n4=n0+1;n1+=function(n4,arr2){for(var n9=0,ele2,n13,n11=arr2.length,n10="";n9<n11;n9++){ele2=arr2[n9],n13=n9+1;n10+="inner loop iterator: "+n13+" parent loop iterator: "+n4} return n10}(n4,arr2)} return n1}'
    """
    expected_node_classname = 'ForNode'
    def _init_vars(self):
        self.for_iterator_varname = self.context.create_new_var('local')
        self.loop_val_varname = self.context.create_new_var('local')
        self.sequence_size_varname = self.context.create_new_var('local')
        self.sequence_size_varname_minus_1 = self.context.create_new_var('local')
        self._check_parent_for_loop_vars()

        #i.e. {% for(loopvar in loop) %}
        self.loopvar = self.django_node.loopvars[0]
        self.context.register_var(self.loopvar, 'local')
        #whether or not we should read the array in reverse
        self.is_reversed = self.django_node.is_reversed
        #variable name of the array to loop
        self.sequence = self._extract_filter_expression(self.django_node.sequence)
        self._init_for_loop_vars_and_rename_in_child()

    def _init_for_loop_vars_and_rename_in_child(self):
        #when the child nodes reference the forloop variables, we need to set the variable values in the for loop
        #we also rename the variable names to something shorter
        #instead of creating a new variable for forloop.counter, we can just use the for loop iterator
        self.context.rename_vars['forloop.counter0'] = self.for_iterator_varname 
        self.forloop_counter_varname = self.context.create_new_var('local')
        self.context.rename_vars['forloop.counter'] = self.forloop_counter_varname
        self.forloop_revcounter_varname = self.context.create_new_var('local')
        self.context.rename_vars['forloop.revcounter'] = self.forloop_revcounter_varname
        self.forloop_revcounter0_varname = self.context.create_new_var('local')
        self.context.rename_vars['forloop.revcounter0'] = self.forloop_revcounter0_varname
        self.forloop_first_varname = self.context.create_new_var('local')
        self.context.rename_vars['forloop.first'] = self.forloop_first_varname
        self.forloop_last_varname = self.context.create_new_var('local')
        self.context.rename_vars['forloop.last'] = self.forloop_last_varname

    def _check_parent_for_loop_vars(self):
        #detect if there is a parent forloop with loopvars, if so, then make sure all
        #references to the parent loopvars e.g. forloop.parentloop.counter are set 
        #to the corresponding varname
        if self.parent_js_node:
            if 'forloop.counter' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.counter'] = self.parent_js_node.context.rename_vars['forloop.counter']
            if 'forloop.counter0' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.counter0'] = self.parent_js_node.context.rename_vars['forloop.counter0']
            if 'forloop.revcounter' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.revcounter'] = self.parent_js_node.context.rename_vars['forloop.revcounter']
            if 'forloop.revcounter0' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.revcounter0'] = self.parent_js_node.context.rename_vars['forloop.revcounter0']
            if 'forloop.first' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.first'] = self.parent_js_node.context.rename_vars['forloop.first']
            if 'forloop.last' in self.parent_js_node.context.rename_vars:
                self.context.rename_vars['forloop.parentloop.last'] = self.parent_js_node.context.rename_vars['forloop.last']
    def _init_sub_nodes(self):
        self.loop_block = self.scan_section(self.django_node.nodelist_loop)
        self.empty_block = None
        if len(self.django_node.nodelist_empty):
            self.empty_block = self.scan_section(self.django_node.nodelist_empty)
    def generate_js_statement(self):
        #length of for loop array e.g. arrlen=arr.length
        sequence_size_init = self.sequence_size_varname + '=' + self.sequence + '.length'
        forloop_info_vars = {}
        #check if any of the forloop variables were called in the child nodes
        #if so, then make sure we actually define them, if not, then we can save a some cycles and a few lines of
        #javascript code by not defining them
        if self.forloop_counter_varname in self.context.vars_used_in_children:
            forloop_info_vars[self.forloop_counter_varname] = self.for_iterator_varname + '+1'
        if self.forloop_revcounter_varname in self.context.vars_used_in_children:
            forloop_info_vars[self.forloop_revcounter_varname] = self.sequence_size_varname + '-' + self.for_iterator_varname + '-1'
        if self.forloop_revcounter0_varname in self.context.vars_used_in_children:
            forloop_info_vars[self.forloop_revcounter0_varname] = self.sequence_size_varname + '-' + self.for_iterator_varname
        if self.forloop_first_varname in self.context.vars_used_in_children:
            forloop_info_vars[self.forloop_first_varname] = '(' + self.for_iterator_varname + '==' + '0)'
        if self.forloop_last_varname in self.context.vars_used_in_children:
            forloop_info_vars[self.forloop_last_varname] = '(' + self.for_iterator_varname + '==' + self.sequence_size_varname_minus_1 + ')'
            sequence_size_init += ',' + self.sequence_size_varname_minus_1 + '=' + self.sequence_size_varname + '-1'

        #initialization variables for for loop e.g. for(var initvar1=0, initvar2; ...)
        for_init_vars = [self.for_iterator_varname + '=0', self.loopvar]
        js_loop_vars = [self.loopvar + '=' + self.sequence + '[' + self.for_iterator_varname + ']']
        #if any of the forloop_info_vars are set, we create their javascript strings here
        if forloop_info_vars:
            #e.g. counter0=i-1,rev_counter=arrSize-i,...
            js_loop_vars.append(','.join(['='.join(var_val) for var_val in forloop_info_vars.items()]))
            #initialize the variables in the for init
            for_init_vars.extend(forloop_info_vars.keys())

        if self.empty_block:
            empty_block_init = 'var ' + sequence_size_init + ';'
        else:
            for_init_vars.append(sequence_size_init)
            
        if JsTplSettings.CONFIG['VERSAGER_MODE']:
            for_init_vars.append(self.loop_val_varname + '=[]')
            loop_val = self.loop_val_varname + '[' + self.loop_val_varname + '.length]=' \
                + self._nodes_to_js_str(self.loop_block, as_closure = True)
            loop_val_result = self.loop_val_varname + '.join("")'
        else:
            for_init_vars.append(self.loop_val_varname + '=""')
            loop_val = self.loop_val_varname + '+=' + self._nodes_to_js_str(self.loop_block, as_closure = True)
            loop_val_result = self.loop_val_varname

        for_init = 'var ' +  ','.join(for_init_vars) + ';'
        #e.g. for(...; i < arraySize; ...)
        for_check = self.for_iterator_varname + '<' + self.sequence_size_varname + ';'
        #e.g. for(..; ...; i++)
        for_increment = self.for_iterator_varname + '++'
        
        for_stmt = 'for(' + for_init + for_check + for_increment + '){' + ','.join(js_loop_vars) + ';' + \
            loop_val + '} return ' + loop_val_result
        #if empty block is set, then we wrap the for statement inside of if statement that tests whether or not the 
        #sequence is empty
        if self.empty_block:
            for_stmt = empty_block_init + 'if(' + self.sequence_size_varname + '){' + for_stmt + \
                '}else{' + self._nodes_to_js_str(self.empty_block) + '}'
        return for_stmt

JsProcessorRegistry.register_js_node(ForJsNode)