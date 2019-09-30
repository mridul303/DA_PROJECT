# To test the code we need access to the flaskr module which is in another
# folder. Since relative imports doesn't work in python 3 and above, this
# only workaround where we append the top level folder(wihch has flaskr and
# tests directories) as the parent folder in order to gain access to the
# flaskr module.
#
# The get_root package is imported by other modules in the tests package if
# they need acces to the modules in the flaskr package. Defining the path here
# once is better than redefining it in every module that requires it.
#
# CURRENT_PATH is the absolute path for this __init__.py file.
# ROOT builds on current path to reach the top level folder.

import os
import sys

CURRENT_PATH = os.path.realpath(__file__)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_PATH)))
sys.path.append(ROOT)
