#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

#Boiler plate Django environment setup
import os
import sys

CURRENT_PATH = os.path.dirname(__file__)
DJANGO_DIRECTORY_PATH = os.path.join(CURRENT_PATH, '../../../')
sys.path.append(DJANGO_DIRECTORY_PATH)

import manage
import settings

#Load files necessary for our specific task
from yz_js_django_tpl import generate_js_tpl_file, JsTplSettings
from yz_js_django_tpl.customtags import *
from yz_js_django_tpl.customfilters import *
import os

template_generator_configs = {
    'demo_config' : {
        'VERSAGER_MODE': False,
        #definition for filters that are used
        'js_dependencies_location' : CURRENT_PATH + '/generated_js/helper_functions_for_js_templates.js',
        'generated_js_file_location': CURRENT_PATH + '/generated_js/generated_js_templates.js',
        'tpls': {
            'test_tpl1.html' : {
            'tpl_func_name': 'yz_djstpl_test_tpl1',
            'var_list': ['comment','server_or_client_side']
            }
        }
    }
}

JsTplSettings.init_config(template_generator_configs['demo_config'])
generate_js_tpl_file()
