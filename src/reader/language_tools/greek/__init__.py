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
                        ('*A',     u'Α'),
                        ('*B',     u'Β'),
                        ('*G',     u'Γ'),
                        ('*D',     u'Δ'),
                        ('*E',     u'Ε'),
                        ('*Z',     u'Ζ'),
                        ('*H',     u'Η'),
                        ('*Q',     u'Θ'),
                        ('*I',     u'Ι'),
                        ('*K',     u'Κ'),
                        ('*L',     u'Λ'),
                        ('*M',     u'Μ'),
                        ('*N',     u'Ν'),
                        ('*C',     u'Ξ'),
                        ('*O',     u'Ο'),
                        ('*P',     u'Π'),
                        ('*R',     u'Ρ'),
                        ('*S',     u'Σ'),
                        ('*T',     u'Τ'),
                        ('*U',     u'Υ'),
                        ('*F',     u'Φ'),
                        ('*X',     u'Χ'),
                        ('*Y',     u'Ψ'),
                        ('*W',     u'Ω'),
                        ('A',      u'α'),
                        ('B',      u'β'),
                        ('G',      u'γ'),
                        ('D',      u'δ'),
                        ('E',      u'ε'),
                        ('Z',      u'ζ'),
                        ('H',      u'η'),
                        ('Q',      u'θ'),
                        ('I',      u'ι'),
                        ('K',      u'κ'),
                        ('L',      u'λ'),
                        ('M',      u'μ'),
                        ('N',      u'ν'),
                        ('C',      u'ξ'),
                        ('O',      u'ο'),
                        ('P',      u'π'),
                        ('R',      u'ρ'),
                        ('S',      u'σ'),
                        ('T',      u'τ'),
                        ('U',      u'υ'),
                        ('F',      u'φ'),
                        ('X',      u'χ'),
                        ('Y',      u'ψ'),
                        ('W',      u'ω'),
                        ('I+',     u'ϊ'),
                        ('U+',     u'ϋ'),
                        ('A)',     u'ἀ'),
                        ('A(',     u'ἁ'),
                        ('A)\\',   u'ἂ'),
                        ('A(\\',   u'ἃ'),
                        ('A)/',    u'ἄ'),
                        ('A(/',    u'ἅ'),
                        ('E)',     u'ἐ'),
                        ('E(',     u'ἑ'),
                        ('E)\\',   u'ἒ'),
                        ('E(\\',   u'ἓ'),
                        ('E)/',    u'ἔ'),
                        ('E(/',    u'ἕ'),
                        ('H)',     u'ἠ'),
                        ('H(',     u'ἡ'),
                        ('H)\\',   u'ἢ'),
                        ('H(\\',   u'ἣ'),
                        ('H)/',    u'ἤ'),
                        ('H(/',    u'ἥ'),
                        ('I)',     u'ἰ'),
                        ('I(',     u'ἱ'),
                        ('I)\\',   u'ἲ'),
                        ('I(\\',   u'ἳ'),
                        ('I)/',    u'ἴ'),
                        ('I(/',    u'ἵ'),
                        ('O)',     u'ὀ'),
                        ('O(',     u'ὁ'),
                        ('O)\\',   u'ὂ'),
                        ('O(\\',   u'ὃ'),
                        ('O)/',    u'ὄ'),
                        ('O(/',    u'ὅ'),
                        ('U)',     u'ὐ'),
                        ('U(',     u'ὑ'),
                        ('U)\\',   u'ὒ'),
                        ('U(\\',   u'ὓ'),
                        ('U)/',    u'ὔ'),
                        ('U(/',    u'ὕ'),
                        ('W)',     u'ὠ'),
                        ('W(',     u'ὡ'),
                        ('W)\\',   u'ὢ'),
                        ('W(\\',   u'ὣ'),
                        ('W)/',    u'ὤ'),
                        ('W(/',    u'ὥ'),
                        ('A)=',    u'ἆ'),
                        ('A(=',    u'ἇ'),
                        ('H)=',    u'ἦ'),
                        ('H(=',    u'ἧ'),
                        ('I)=',    u'ἶ'),
                        ('I(=',    u'ἷ'),
                        ('U)=',    u'ὖ'),
                        ('U(=',    u'ὗ'),
                        ('W)=',    u'ὦ'),
                        ('W(=',    u'ὧ'),
                        ('*A)',    u'Ἀ'),
                        ('*)A',    u'Ἀ'),
                        ('*A(',    u'Ἁ'),
                        ('*(A',    u'Ἁ'),
                        ('*(\\A',  u'Ἃ'),
                        ('*A)/',   u'Ἄ'),
                        ('*)/A',   u'Ἄ'),
                        ('*A(/',   u'Ἇ'),
                        ('*(/A',   u'Ἇ'),
                        ('*E)',    u'Ἐ'),
                        ('*)E',    u'Ἐ'),
                        ('*E(',    u'Ἑ'),
                        ('*(E',    u'Ἑ'),
                        ('*(\\E',  u'Ἓ'),
                        ('*E)/',   u'Ἔ'),
                        ('*)/E',   u'Ἔ'),
                        ('*E(/',   u'Ἕ'),
                        ('*(/E',   u'Ἕ'),
                        ('*H)',    u'Ἠ'),
                        ('*)H',    u'Ἠ'),
                        ('*H(',    u'Ἡ'),
                        ('*(H',    u'Ἡ'),
                        ('*H)\\',  u'Ἢ'),
                        (')\\*H',  u'Ἢ'),
                        ('*)\\H',  u'Ἢ'),
                        ('*H)/',   u'Ἤ'),
                        ('*)/H',   u'Ἤ'),
                        ('*)=H',   u'Ἦ'),
                        ('(/*H',   u'Ἧ'),
                        ('*(/H',   u'Ἧ'),
                        ('*I)',    u'Ἰ'),
                        ('*)I',    u'Ἰ'),
                        ('*I(',    u'Ἱ'),
                        ('*(I',    u'Ἱ'),
                        ('*I)/',   u'Ἴ'),
                        ('*)/I',   u'Ἴ'),
                        ('*I(/',   u'Ἷ'),
                        ('*(/I',   u'Ἷ'),
                        ('*O)',    u'Ὀ'),
                        ('*)O',    u'Ὀ'),
                        ('*O(',    u'Ὁ'),
                        ('*(O',    u'Ὁ'),
                        ('*(\\O',  u'Ὃ'),
                        ('*O)/',   u'Ὄ'),
                        ('*)/O',   u'Ὄ'),
                        ('*O(/',   u'Ὅ'),
                        ('*(/O',   u'Ὅ'),
                        ('*U(',    u'Ὑ'),
                        ('*(U',    u'Ὑ'),
                        ('*(/U',   u'Ὕ'),
                        ('*(=U',   u'Ὗ'),
                        ('*W)',    u'Ὠ'),
                        ('*W(',    u'Ὡ'),
                        ('*(W',    u'Ὡ'),
                        ('*W)/',   u'Ὤ'),
                        ('*)/W',   u'Ὤ'),
                        ('*W(/',   u'Ὧ'),
                        ('*(/W',   u'Ὧ'),
                        ('*A)=',   u'Ἆ'),
                        ('*)=A',   u'Ἆ'),
                        ('*A(=',   u'Ἇ'),
                        ('*W)=',   u'Ὦ'),
                        ('*)=W',   u'Ὦ'),
                        ('*W(=',   u'Ὧ'),
                        ('*(=W',   u'Ὧ'),
                        ('A\\',    u'ὰ'),
                        ('A/',     u'ά'),
                        ('E\\',    u'ὲ'),
                        ('E/',     u'έ'),
                        ('H\\',    u'ὴ'),
                        ('H/',     u'ή'),
                        ('I\\',    u'ὶ'),
                        ('I/',     u'ί'),
                        ('O\\',    u'ὸ'),
                        ('O/',     u'ό'),
                        ('U\\',    u'ὺ'),
                        ('U/',     u'ύ'),
                        ('W\\',    u'ὼ'),
                        ('W/',     u'ώ'),
                        ('A)/|',   u'ᾄ'),
                        ('A(/|',   u'ᾅ'),
                        ('H)|',    u'ᾐ'),
                        ('H(|',    u'ᾑ'),
                        ('H)/|',   u'ᾔ'),
                        ('H)=|',   u'ᾖ'),
                        ('H(=|',   u'ᾗ'),
                        ('W)|',    u'ᾠ'),
                        ('W(=|',   u'ᾧ'),
                        ('A=',     u'ᾶ'),
                        ('H=',     u'ῆ'),
                        ('I=',     u'ῖ'),
                        ('U=',     u'ῦ'),
                        ('W=',     u'ῶ'),
                        ('I\\+',   u'ῒ'),
                        ('I/+',    u'ΐ'),
                        ('I+/',    u'ΐ'),
                        ('U\\+',   u'ῢ'),
                        ('U/+',    u'ΰ'),
                        ('A|',     u'ᾳ'),
                        ('A/|',    u'ᾴ'),
                        ('H|',     u'ῃ'),
                        ('H/|',    u'ῄ'),
                        ('W|',     u'ῳ'),
                        ('W|/',    u'ῴ'),
                        ('W/|',    u'ῴ'),
                        ('A=|',    u'ᾷ'),
                        ('H=|',    u'ῇ'),
                        ('W=|',    u'ῷ'),
                        ('R(',     u'ῤ'),
                        ('*R(',    u'Ῥ'),
                        ('*(R',    u'Ῥ'),
                        
                        (')',    u'ʼ'),
                        
                        #Breve
                        ("A'",     u'ᾰ'),
                        
                        # The following are only necessary for back-converting to Greek
                        ('S',      u'ς'), #Final sigma
                        ('E/',     u'έ'),
                        ('A/',     u'ά'),
                        ('H/',     u'ή'),
                        ('O/',     u'ό'),
                        ('I/',     u'ί'),
                        ('U/',     u'ύ'),
                        ('W/',     u'ώ')
                        
                       ]
    
    ENDING_SIGMA_RE = re.compile(u"(σ(?=\Z))|(σ(?=[^\w]))",re.UNICODE)
    
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
        
        return Greek.beta_code_to_unicode(unicode(beta_code_string, "UTF-8", mode))
    
    @staticmethod
    def fix_final_sigma(greek_unicode):
        return Greek.ENDING_SIGMA_RE.sub(u"ς", greek_unicode)
    
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
        
        return Greek.unicode_to_beta_code(greek_unicode_string).encode("ascii", mode)
