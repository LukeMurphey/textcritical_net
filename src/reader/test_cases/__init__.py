import os
import time
import unittest
from django.test import TestCase

class TestReader(TestCase):
    
    def get_test_resource_directory(self):
        return os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test_files')

    def get_test_resource_file_name(self, file_name):
        return os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test_files', file_name)
    
    def write_out_test_file(self, content):
        
        fname = '/Users/lmurphey/Desktop/output.txt'
        f = open(fname, 'w')
        f.write(content)
        f.close()
    
    def load_test_resource(self, file_name):
        
        f = None
        
        try:
            f = open(self.get_test_resource_file_name(file_name), 'r')
            return f.read()
        finally:
            if f is not None:
                f.close()

def time_function_call(fx):
    """
    This decorator will provide a log message measuring how long a function call took.
    
    Arguments:
    fx -- The function to measure
    """
    
    def wrapper(*args, **kwargs):
        t = time.time()
        
        r = fx(*args, **kwargs)
        
        diff = time.time() - t
        
        diff_string = str(round(diff, 6)) + " seconds"
        
        print("%s, duration=%s" % (fx.__name__, diff_string))
        
        return r
    return wrapper

# unittest.TestLoader will call this when it finds this module:
"""
def load_tests(*args, **kwargs):
  test_all_doctests = unittest.TestSuite()
  for m in DOCTEST_MODULES:
    test_all_doctests.addTest(doctest.DocTestSuite(m))
  return test_all_doctests
"""