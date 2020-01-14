# -*- coding: utf8 -*-
'''
Created on Aug 30, 2012

@author: Luke Murphey
'''

import re

class Greek():
    """
    Provides various helper functions for managing Greek text.
    
    In particular, this class provides methods for converting beta-code representation to 
    unicode (see http://en.wikipedia.org/wiki/Beta_code).
    
    A complete list of the beta-codes are available here: http://www.tlg.uci.edu/encoding/quickbeta.pdf
    """
    
    BETA_CODE_TABLE = [
                        ('*A',     'Α'),
                        ('*B',     'Β'),
                        ('*G',     'Γ'),
                        ('*D',     'Δ'),
                        ('*E',     'Ε'),
                        ('*Z',     'Ζ'),
                        ('*H',     'Η'),
                        ('*Q',     'Θ'),
                        ('*I',     'Ι'),
                        ('*K',     'Κ'),
                        ('*L',     'Λ'),
                        ('*M',     'Μ'),
                        ('*N',     'Ν'),
                        ('*C',     'Ξ'),
                        ('*O',     'Ο'),
                        ('*P',     'Π'),
                        ('*R',     'Ρ'),
                        ('*S',     'Σ'),
                        ('*T',     'Τ'),
                        ('*U',     'Υ'),
                        ('*F',     'Φ'),
                        ('*X',     'Χ'),
                        ('*Y',     'Ψ'),
                        ('*W',     'Ω'),
                        ('A',      'α'),
                        ('B',      'β'),
                        ('G',      'γ'),
                        ('D',      'δ'),
                        ('E',      'ε'),
                        ('Z',      'ζ'),
                        ('H',      'η'),
                        ('Q',      'θ'),
                        ('I',      'ι'),
                        ('K',      'κ'),
                        ('L',      'λ'),
                        ('M',      'μ'),
                        ('N',      'ν'),
                        ('C',      'ξ'),
                        ('O',      'ο'),
                        ('P',      'π'),
                        ('R',      'ρ'),
                        ('S',      'σ'),
                        ('T',      'τ'),
                        ('U',      'υ'),
                        ('F',      'φ'),
                        ('X',      'χ'),
                        ('Y',      'ψ'),
                        ('W',      'ω'),
                        ('I+',     'ϊ'),
                        ('U+',     'ϋ'),
                        ('A)',     'ἀ'),
                        ('A(',     'ἁ'),
                        ('A)\\',   'ἂ'),
                        ('A(\\',   'ἃ'),
                        ('A)/',    'ἄ'),
                        ('A(/',    'ἅ'),
                        ('E)',     'ἐ'),
                        ('E(',     'ἑ'),
                        ('E)\\',   'ἒ'),
                        ('E(\\',   'ἓ'),
                        ('E)/',    'ἔ'),
                        ('E(/',    'ἕ'),
                        ('H)',     'ἠ'),
                        ('H(',     'ἡ'),
                        ('H)\\',   'ἢ'),
                        ('H(\\',   'ἣ'),
                        ('H)/',    'ἤ'),
                        ('H(/',    'ἥ'),
                        ('I)',     'ἰ'),
                        ('I(',     'ἱ'),
                        ('I)\\',   'ἲ'),
                        ('I(\\',   'ἳ'),
                        ('I)/',    'ἴ'),
                        ('I(/',    'ἵ'),
                        ('O)',     'ὀ'),
                        ('O(',     'ὁ'),
                        ('O)\\',   'ὂ'),
                        ('O(\\',   'ὃ'),
                        ('O)/',    'ὄ'),
                        ('O(/',    'ὅ'),
                        ('U)',     'ὐ'),
                        ('U(',     'ὑ'),
                        ('U)\\',   'ὒ'),
                        ('U(\\',   'ὓ'),
                        ('U)/',    'ὔ'),
                        ('U(/',    'ὕ'),
                        ('W)',     'ὠ'),
                        ('W(',     'ὡ'),
                        ('W)\\',   'ὢ'),
                        ('W(\\',   'ὣ'),
                        ('W)/',    'ὤ'),
                        ('W(/',    'ὥ'),
                        ('A)=',    'ἆ'),
                        ('A(=',    'ἇ'),
                        ('H)=',    'ἦ'),
                        ('H(=',    'ἧ'),
                        ('I)=',    'ἶ'),
                        ('I(=',    'ἷ'),
                        ('U)=',    'ὖ'),
                        ('U(=',    'ὗ'),
                        ('W)=',    'ὦ'),
                        ('W(=',    'ὧ'),
                        ('*A)',    'Ἀ'),
                        ('*)A',    'Ἀ'),
                        ('*A(',    'Ἁ'),
                        ('*(A',    'Ἁ'),
                        ('*(\\A',  'Ἃ'),
                        ('*A)/',   'Ἄ'),
                        ('*)/A',   'Ἄ'),
                        ('*A(/',   'Ἇ'),
                        ('*(/A',   'Ἇ'),
                        ('*E)',    'Ἐ'),
                        ('*)E',    'Ἐ'),
                        ('*E(',    'Ἑ'),
                        ('*(E',    'Ἑ'),
                        ('*(\\E',  'Ἓ'),
                        ('*E)/',   'Ἔ'),
                        ('*)/E',   'Ἔ'),
                        ('*E(/',   'Ἕ'),
                        ('*(/E',   'Ἕ'),
                        ('*H)',    'Ἠ'),
                        ('*)H',    'Ἠ'),
                        ('*H(',    'Ἡ'),
                        ('*(H',    'Ἡ'),
                        ('*H)\\',  'Ἢ'),
                        (')\\*H',  'Ἢ'),
                        ('*)\\H',  'Ἢ'),
                        ('*H)/',   'Ἤ'),
                        ('*)/H',   'Ἤ'),
                        ('*)=H',   'Ἦ'),
                        ('(/*H',   'Ἧ'),
                        ('*(/H',   'Ἧ'),
                        ('*I)',    'Ἰ'),
                        ('*)I',    'Ἰ'),
                        ('*I(',    'Ἱ'),
                        ('*(I',    'Ἱ'),
                        ('*I)/',   'Ἴ'),
                        ('*)/I',   'Ἴ'),
                        ('*I(/',   'Ἷ'),
                        ('*(/I',   'Ἷ'),
                        ('*O)',    'Ὀ'),
                        ('*)O',    'Ὀ'),
                        ('*O(',    'Ὁ'),
                        ('*(O',    'Ὁ'),
                        ('*(\\O',  'Ὃ'),
                        ('*O)/',   'Ὄ'),
                        ('*)/O',   'Ὄ'),
                        ('*O(/',   'Ὅ'),
                        ('*(/O',   'Ὅ'),
                        ('*U(',    'Ὑ'),
                        ('*(U',    'Ὑ'),
                        ('*(/U',   'Ὕ'),
                        ('*(=U',   'Ὗ'),
                        ('*W)',    'Ὠ'),
                        ('*W(',    'Ὡ'),
                        ('*(W',    'Ὡ'),
                        ('*W)/',   'Ὤ'),
                        ('*)/W',   'Ὤ'),
                        ('*W(/',   'Ὧ'),
                        ('*(/W',   'Ὧ'),
                        ('*A)=',   'Ἆ'),
                        ('*)=A',   'Ἆ'),
                        ('*A(=',   'Ἇ'),
                        ('*W)=',   'Ὦ'),
                        ('*)=W',   'Ὦ'),
                        ('*W(=',   'Ὧ'),
                        ('*(=W',   'Ὧ'),
                        ('A\\',    'ὰ'),
                        ('A/',     'ά'),
                        ('E\\',    'ὲ'),
                        ('E/',     'έ'),
                        ('H\\',    'ὴ'),
                        ('H/',     'ή'),
                        ('I\\',    'ὶ'),
                        ('I/',     'ί'),
                        ('O\\',    'ὸ'),
                        ('O/',     'ό'),
                        ('U\\',    'ὺ'),
                        ('U/',     'ύ'),
                        ('W\\',    'ὼ'),
                        ('W/',     'ώ'),
                        ('A)/|',   'ᾄ'),
                        ('A(/|',   'ᾅ'),
                        ('H)|',    'ᾐ'),
                        ('H(|',    'ᾑ'),
                        ('H)/|',   'ᾔ'),
                        ('H)=|',   'ᾖ'),
                        ('H(=|',   'ᾗ'),
                        ('W)|',    'ᾠ'),
                        ('W(=|',   'ᾧ'),
                        ('A=',     'ᾶ'),
                        ('H=',     'ῆ'),
                        ('I=',     'ῖ'),
                        ('U=',     'ῦ'),
                        ('W=',     'ῶ'),
                        ('I\\+',   'ῒ'),
                        ('I/+',    'ΐ'),
                        ('I+/',    'ΐ'),
                        ('U\\+',   'ῢ'),
                        ('U/+',    'ΰ'),
                        ('A|',     'ᾳ'),
                        ('A/|',    'ᾴ'),
                        ('H|',     'ῃ'),
                        ('H/|',    'ῄ'),
                        ('W|',     'ῳ'),
                        ('W|/',    'ῴ'),
                        ('W/|',    'ῴ'),
                        ('A=|',    'ᾷ'),
                        ('H=|',    'ῇ'),
                        ('W=|',    'ῷ'),
                        ('R(',     'ῤ'),
                        ('*R(',    'Ῥ'),
                        ('*(R',    'Ῥ'),
                        
                        (')',    'ʼ'),
                        
                        #Breve
                        ("A'",     'ᾰ'),
                        
                        # The following are only necessary for back-converting to Greek
                        ('S',      'ς'), #Final sigma
                        ('E/',     'έ'),
                        ('A/',     'ά'),
                        ('H/',     'ή'),
                        ('O/',     'ό'),
                        ('I/',     'ί'),
                        ('U/',     'ύ'),
                        ('W/',     'ώ')
                        
                       ]
    
    ENDING_SIGMA_RE = re.compile("(σ(?=\Z))|(σ(?=[^\w]))",re.UNICODE)
    
    ordered_code_table = None
    
    @staticmethod
    def __get_ordered_code_table__():
        """
        Get the code table sorted by the length of the beta-code entry with the largest first.
        """
        
        if Greek.ordered_code_table is None:
            Greek.ordered_code_table = sorted(Greek.BETA_CODE_TABLE, key=lambda entry: 10 - len(entry[0]))
    
        return Greek.ordered_code_table
    
    @staticmethod
    def beta_code_str_to_unicode(beta_code_string, mode='strict'):
        """
        Convert the beta code into unicode. The input string with be assumed to be a str.
        
        The object returned is a unicode object, you may need to convert it to a string
        (using something like "beta_code_string.encode('utf-8')").
        
        Arguments:
        beta_code_string -- A string representing beta-code for Greek
        mode -- The mode for handling invalid characters; can be 'strict', 'ignore', 'xmlcharrefreplace', and 'replace
        """
        # TODO: determine what to do with mode
        return Greek.beta_code_to_unicode(beta_code_string)
    
    @staticmethod
    def fix_final_sigma(greek_unicode):
        return Greek.ENDING_SIGMA_RE.sub("ς", greek_unicode)
    
    @staticmethod
    def beta_code_to_unicode(beta_code_string):
        """
        Convert the beta code into unicode. The input string must be a unicode object.
        
        The object returned is a unicode object, you may need to convert it to a string
        (using something like "beta_code_string.encode('utf-8')").
        
        Arguments:
        beta_code_string -- A string representing beta-code for Greek
        """
        
        # Make sure that the input is in the upper case since we only convert upper case chars
        # This is necessary because Perseus texts are in lower case (but should be upper case)
        beta_code_string = beta_code_string.upper()
        
        # We need to sort the code table such that the largest entries are first
        beta_code_table = Greek.__get_ordered_code_table__()
        
        # Convert each entry
        for beta_char, greek_char in beta_code_table:
            beta_code_string = beta_code_string.replace(beta_char, greek_char)
    
        # Fix the ending sigmas (i.e. change "λογοσ" to "λογος")
        beta_code_string = Greek.fix_final_sigma(beta_code_string)
        
        # Return the encoded result
        return beta_code_string

    @staticmethod
    def unicode_to_beta_code(greek_unicode_string):
        """
        Convert the unicode back into beta-code. The returned object will be a unicode object.
        
        Arguments:
        greek_unicode_string -- A string containing Greek
        """
        
        # Convert each entry
        for beta_char, greek_char in Greek.BETA_CODE_TABLE:
            greek_unicode_string = greek_unicode_string.replace(greek_char, beta_char)
            
        return greek_unicode_string
        
    @staticmethod
    def unicode_to_beta_code_str(greek_unicode_string, mode='replace'):
        """
        Convert the unicode back into beta-code. The returned object will be a string object.
        
        Arguments:
        greek_unicode_string -- A string containing Greek
        mode -- The mode for handling invalid characters; can be 'strict', 'ignore', 'xmlcharrefreplace', and 'replace
        """
        
        # TODO: determine what to do with mode
        return Greek.unicode_to_beta_code(greek_unicode_string)
