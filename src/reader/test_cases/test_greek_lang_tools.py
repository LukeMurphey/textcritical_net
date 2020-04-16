from reader.language_tools.greek import Greek
from reader import language_tools
from . import TestReader

class TestGreekLanguageTools(TestReader):
    
    def test_strip_accents(self):
        self.assertEqual(language_tools.normalize_unicode(language_tools.strip_accents("θεός")), "θεος")
        
    def test_strip_accents_str(self):
        self.assertEqual(language_tools.normalize_unicode("θεός"), "θεός")
    
    def test_beta_code_conversion(self):
        self.assertEqual(Greek.beta_code_str_to_unicode("H)/LIOS"), "ἤλιος")

    def test_beta_code_conversion_unicode(self):
        self.assertEqual(Greek.beta_code_to_unicode("H)/LIOS"), "ἤλιος")
        
    def test_beta_code_conversion_sigmas(self):
        self.assertEqual(Greek.beta_code_to_unicode("O( KO/SMOS"), "ὁ κόσμος")
        
    def test_unicode_conversion_to_beta_code(self):
        self.assertEqual(Greek.unicode_to_beta_code("ἤλιος"), "H)/LIOS")
        
    def test_unicode_conversion_to_beta_code_str(self):
        self.assertEqual(Greek.unicode_to_beta_code_str("ἤλιος"), "H)/LIOS")
        
    def test_section_of_text(self):
        
        # The first verse of Josephus' "Against Apion"
        input = """*(ikanw=s me\\n u(polamba/nw kai\\ dia\\ th=s peri\\ th\\n a)rxaiologi/an 
suggrafh=s, kra/tiste a)ndrw=n *)epafro/dite, toi=s e)nteucome/nois au)th=| 
pepoihke/nai fanero\\n peri\\ tou= ge/nous h(mw=n tw=n *)ioudai/wn, o(/ti kai\\ 
palaio/tato/n e)sti kai\\ th\\n prw/thn u(po/stasin e)/sxen i)di/an, kai\\ pw=s 
th\\n xw/ran h(\\n nu=n e)/xomen katw/|khse &ast; pentakisxili/wn e)tw=n a)riqmo\\n 
i(stori/an perie/xousan e)k tw=n par' h(mi=n i(erw=n bi/blwn dia\\ th=s *(ellhnikh=s
fwnh=s sunegraya/mhn."""

        expected_output = """Ἱκανῶς μὲν ὑπολαμβάνω καὶ διὰ τῆς περὶ τὴν ἀρχαιολογίαν 
συγγραφῆς, κράτιστε ἀνδρῶν Ἐπαφρόδιτε, τοῖς ἐντευξομένοις αὐτῇ 
πεποιηκέναι φανερὸν περὶ τοῦ γένους ἡμῶν τῶν Ἰουδαίων, ὅτι καὶ 
παλαιότατόν ἐστι καὶ τὴν πρώτην ὑπόστασιν ἔσχεν ἰδίαν, καὶ πῶς 
τὴν χώραν ἣν νῦν ἔχομεν κατῴκησε &αστ; πεντακισχιλίων ἐτῶν ἀριθμὸν 
ἱστορίαν περιέχουσαν ἐκ τῶν παρ' ἡμῖν ἱερῶν βίβλων διὰ τῆς Ἑλληνικῆς
φωνῆς συνεγραψάμην."""

        output = Greek.beta_code_str_to_unicode(input)
        
        self.assertEquals(output, expected_output)
        
    def test_various_beta_code_conversions(self):
        
        TEST_BETA_CODES = [
                           ('KAI\\', 'καὶ'),
                           ('KAT)', 'κατʼ'),
                           ('*KAI E)GE/NETO E)N TW=| TETA/RTOW', None), #Και ἐγένετο ἐν τῷ τετάρτῳ
                           ('STH/SAI', 'στήσαι'),
                           
                           # Alternate versions of the acute
                           ('A/E/H/O/I/U/W/', None) #άέήόίύώ
                          ]

        for beta_original, greek_expected in TEST_BETA_CODES:
            greek_actual = Greek.beta_code_to_unicode(beta_original)
            
            if greek_expected is not None:
                self.assertEqual(greek_expected, greek_actual)
            
            beta_actual = Greek.unicode_to_beta_code_str(greek_actual)
            
            self.assertEqual(beta_original, beta_actual)
            
    def test_fix_final_sigma(self):
        self.assertEqual(Greek.fix_final_sigma("κόσμοσ"), "κόσμος")
