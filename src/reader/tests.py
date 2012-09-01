# -*- coding: utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from reader.language_tools.greek import Greek

class TestGreekLanguageTools(TestCase):
    def test_beta_code_conversion(self):
        self.assertEqual( Greek.beta_code_ascii_to_unicode("H)/LIOS"), u"ἤλιος")

    def test_beta_code_conversion_unicode(self):
        self.assertEqual( Greek.beta_code_to_unicode(u"H)/LIOS"), u"ἤλιος")
        
    def test_beta_code_conversion_sigmas(self):
        self.assertEqual( Greek.beta_code_to_unicode(u"O( KO/SMOS"), u"ὁ κόσμος")
        
    def test_unicode_conversion_to_beta_code(self):
        self.assertEqual( Greek.unicode_to_beta_code(u"ἤλιος"), u"H)/LIOS")
