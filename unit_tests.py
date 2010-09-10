#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

#Boiler plate Django environment setup
import os
import sys
import glob

CURRENT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_PATH, '../..'))

import manage
import settings
import doctest
import unittest
#Load files necessary for our specific task

import yz_js_django_tpl.defaulttags
import yz_js_django_tpl.customtags
import yz_js_django_tpl.customfilters
suite = unittest.TestSuite()
#add default tags to test suite
default_tag_modules_to_test = yz_js_django_tpl.defaulttags.__all__[:]
for mod in default_tag_modules_to_test:
    suite.addTest(doctest.DocTestSuite('yz_js_django_tpl.defaulttags.' + mod))
#add default filters to test suite
default_tag_modules_to_test = yz_js_django_tpl.defaultfilters.__all__[:]
for mod in default_tag_modules_to_test:
    suite.addTest(doctest.DocTestSuite('yz_js_django_tpl.defaultfilters.' + mod))

#add custom tags to test suite
default_tag_modules_to_test = yz_js_django_tpl.customtags.__all__[:]
for mod in default_tag_modules_to_test:
    suite.addTest(doctest.DocTestSuite('yz_js_django_tpl.customtags.' + mod))
#add custom tags to test suite
default_tag_modules_to_test = yz_js_django_tpl.customfilters.__all__[:]
for mod in default_tag_modules_to_test:
    suite.addTest(doctest.DocTestSuite('yz_js_django_tpl.customfilters.' + mod))

runner = unittest.TextTestRunner()
runner.run(suite)
# doctest.testmod(yz_js_django_tpl.defaulttags)