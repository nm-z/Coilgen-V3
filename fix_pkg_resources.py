import os
import sys

def _fix_pkg_resources():
    import pkg_resources
    if isinstance(pkg_resources.working_set, list):
        pkg_resources.working_set = pkg_resources.WorkingSet()

def _fix_xml_import():
    import importlib
    import sys
    
    # Remove any existing 'xml' module from sys.modules
    if 'xml' in sys.modules:
        del sys.modules['xml']
    
    # Import the correct 'xml' module
    xml = importlib.import_module('xml')
    sys.modules['xml'] = xml

_fix_pkg_resources()
_fix_xml_import()