from django.test import TestCase
from textcritical.context_processors import is_async

class TestContextProcessors(TestCase):
    
    class Request(object):
        
        def __init__(self, is_ajax=False, args=None):
            
            if args is not None:
                self.GET = args
            else:
                self.GET = {'param' : 'nothing'}
            
            self.is_ajax_param = is_ajax

            if is_ajax:
                self.META = { 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' }
            else:
                self.META = { 'HTTP_X_REQUESTED_WITH': '' }
    
    def test_is_async(self):
        
        self.assertEqual(is_async(TestContextProcessors.Request(False))['is_async'], False, "Failed to correctly identify non-AJAX request")
        self.assertEqual(is_async(TestContextProcessors.Request(True))['is_async'], True, "Failed to correctly identify AJAX request")
        self.assertEqual(is_async(TestContextProcessors.Request(False, {'async' : None}))['is_async'], True, "Failed to correctly identify async request based on parameter")
        self.assertEqual(is_async(TestContextProcessors.Request(False, {'async' : '1'}))['is_async'], True, "Failed to correctly identify async request based on parameter")
        self.assertEqual(is_async(TestContextProcessors.Request(False, {'async' : '0'}))['is_async'], False, "Failed to correctly identify non-async request based on parameter")
        self.assertEqual(is_async(TestContextProcessors.Request(True, {'async' : '1'}))['is_async'], True, "Failed to correctly identify AJAX request (along with parameter)")
