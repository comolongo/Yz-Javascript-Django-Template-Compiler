#YZ JavaScript Django Template Compiler
#Copyright (c) 2010 Weiss I Nicht <KeineAhnung@atliva.com> 
#(sha-1: 90f01291285340bf03c2d41952c4b21b3d338907)

import os
import glob
__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*JsNode.py")]