#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

from django.conf.urls.defaults import *
import os
CURRENT_PATH = os.path.dirname(__file__)

urlpatterns = patterns('django.views',
    (r'^$', 'generic.simple.direct_to_template', {'template': 'yz_djs_demo.html', 'extra_context' : {
        'comments' : [
            {
                'comment_title': 'I really digg this tool',
                'author'       : 'Wisste Nicht',
                'comment_body' : 'Now I just which somebody else could feel the same way'
            },
            {
                'comment_title': 'Save bandwidth and server load by off loading template construction to client side',
                'author'       : 'Bu Zhidao',
                'comment_body' : 'One template, client and server sides, one parser to unit them all'
            }
        ],
            'server_or_client_side' : 'server'
    }}),
    (r'^js/(?P<path>.*)$', 'static.serve',{'document_root': CURRENT_PATH + '/generated_js'}),
)