# -*- coding: utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


from xml.dom.minidom import parse, parseString
import os

from textcritical.default_settings import SITE_ROOT
from reader.importer.Perseus import PerseusTextImporter
from reader.importer import TextImporter
from reader.language_tools.greek import Greek
from reader.models import Author, Chapter, Verse, Section

class TestGreekLanguageTools(TestCase):
    def test_beta_code_conversion(self):
        self.assertEqual( Greek.beta_code_str_to_unicode("H)/LIOS"), u"ἤλιος")

    def test_beta_code_conversion_unicode(self):
        self.assertEqual( Greek.beta_code_to_unicode(u"H)/LIOS"), u"ἤλιος")
        
    def test_beta_code_conversion_sigmas(self):
        self.assertEqual( Greek.beta_code_to_unicode(u"O( KO/SMOS"), u"ὁ κόσμος")
        
    def test_unicode_conversion_to_beta_code(self):
        self.assertEqual( Greek.unicode_to_beta_code(u"ἤλιος"), u"H)/LIOS")
        
    def test_unicode_conversion_to_beta_code_str(self):
        self.assertEqual( Greek.unicode_to_beta_code_str(u"ἤλιος"), "H)/LIOS")
        
    def test_section_of_text(self):
        
        # The first verse of Josephus' "Against Apion"
        input = """*(ikanw=s me\\n u(polamba/nw kai\\ dia\\ th=s peri\\ th\\n a)rxaiologi/an 
suggrafh=s, kra/tiste a)ndrw=n *)epafro/dite, toi=s e)nteucome/nois au)th=| 
pepoihke/nai fanero\\n peri\\ tou= ge/nous h(mw=n tw=n *)ioudai/wn, o(/ti kai\\ 
palaio/tato/n e)sti kai\\ th\\n prw/thn u(po/stasin e)/sxen i)di/an, kai\\ pw=s 
th\\n xw/ran h(\\n nu=n e)/xomen katw/|khse &ast; pentakisxili/wn e)tw=n a)riqmo\\n 
i(stori/an perie/xousan e)k tw=n par' h(mi=n i(erw=n bi/blwn dia\\ th=s *(ellhnikh=s
fwnh=s sunegraya/mhn."""

        expected_output = u"""Ἱκανῶς μὲν ὑπολαμβάνω καὶ διὰ τῆς περὶ τὴν ἀρχαιολογίαν 
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
                           ('KAI\\', u'καὶ'),
                           ('KAT)', u'κατʼ'),
                           ('*KAI E)GE/NETO E)N TW=| TETA/RTOW', None), #Και ἐγένετο ἐν τῷ τετάρτῳ
                           ('STH/SAI', u'στήσαι'),
                           
                           # Alternate versions of the acute
                           ('A/E/H/O/I/U/W/', None) #άέήόίύώ
                          ]

        for beta_original, greek_expected in TEST_BETA_CODES:
            greek_actual = Greek.beta_code_to_unicode(beta_original)
            
            if greek_expected is not None:
                self.assertEqual( greek_expected, greek_actual)
            
            beta_actual = Greek.unicode_to_beta_code_str(greek_actual)
            
            self.assertEqual( beta_original, beta_actual )
            
class TestImport(TestCase):
     
    def setUp(self):
        self.importer = TextImporter()
     
    def test_make_author(self):
        
        name = "Luke Murphey"
        self.importer.make_author(name)
        self.importer.make_author(name)
        
        self.assertEquals( Author.objects.filter(name=name).count(), 1)
        
    def test_copy_node(self):
        
        src_xml = r"""
            <src>
                <vowels>
                    <a capitol="A">
                        <nocopy />
                    </a>
                </vowels>
            </src>
        """
        
        dst_xml = r"""
            <dst>
                <vowels>
                    <b capitol="B">
                    </b>
                </vowels>
            </dst>
        """
        
        src_dom = parseString(src_xml)
        dst_dom = parseString(dst_xml)
        
        # Get the nodes to copy and the place to copy them to
        node_to_copy = src_dom.getElementsByTagName("a")[0]
        to_copy_to = dst_dom.getElementsByTagName("vowels")[0]
        
        # Create the duplicate
        TextImporter.copy_node(node_to_copy, dst_dom, to_copy_to)

        expected = """<?xml version="1.0" ?><dst>
                <vowels>
                    <b capitol="B">
                    </b>
                <a capitol="A"/></vowels>
            </dst>"""
        
        self.assertEquals(expected, dst_dom.toxml())
        
class TestPerseusImport(TestCase):
    
    def setUp(self):
        self.importer = PerseusTextImporter()
    
    def test_bibl_struct_import(self):
        
        bibl_struct_xml = """<biblStruct>
                              <monogr>
                                <author>Flavius Josephus</author>
                                <title>Flavii Iosephi opera</title>
                                <editor role="editor">B. Niese</editor>
                                <imprint>
                                  <pubPlace>Berlin</pubPlace>
                                  <publisher>Weidmann</publisher>
                                  <date>1890</date>
                                </imprint>
                              </monogr>
                            </biblStruct>"""
    
        bible_struct_document = parseString(bibl_struct_xml)
    
        self.importer.import_info_from_bibl_struct(bible_struct_document)
        
        self.assertEquals(self.importer.work.authors.all()[0].name,"Flavius Josephus")
        self.assertEquals(self.importer.work.title,"Flavii Iosephi opera")
        
    def test_get_language(self):
        
        language_xml = """<language id="greek">Greek</language>"""
        
        lang_document = parseString(language_xml)
        
        language = self.importer.get_language(lang_document)
        
        self.assertEquals(language, "Greek")
        
    def test_get_states(self):
                                    
        states_xml = """ <refsDecl doctype="TEI.2">
                            <state unit="section"/>
                            <state n="chunk" unit="Whiston section"/>
                         </refsDecl>"""
                            
        states_doc = parseString(states_xml)
        
        states = PerseusTextImporter.getStates(states_doc)
        
        self.assertEquals(states[0].name, "section")
        self.assertEquals(states[1].name, "Whiston section")
        self.assertEquals(states[1].section_type, "chunk")
        
    def test_get_chunks(self):
        
        encoding_desc_xml = """ <encodingDesc>
                              <refsDecl doctype="TEI.2">
                            <state unit="section"/>
                              </refsDecl>
                              <refsDecl doctype="TEI.2">
                            <state n="chunk" unit="Whiston section"/>
                              </refsDecl>
                            </encodingDesc>"""
        
        encoding_desc = parseString(encoding_desc_xml)
        
        chunks = PerseusTextImporter.getStateSets(encoding_desc)
        
        self.assertEquals(chunks[0][0].name, "section")
        
        self.assertEquals(chunks[1][0].name, "Whiston section")
        self.assertEquals(chunks[1][0].section_type, "chunk")
    
    def load_test_resource(self, file_name):
        
        f = None
        
        try:
            f = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test', file_name), 'r')
            return f.read()
        finally:
            if f is not None:
                f.close()
    
    def test_load_book(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Flavius Josephus"
        author.save()
        
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        chapters = Chapter.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(chapter=chapters[0])
        
        # Make sure the importer is smart enougn not to make duplicate authors
        self.assertEquals( Author.objects.filter(name="Flavius Josephus").count(), 1)
        self.assertEquals( chapters.count(), 1)
        self.assertEquals( verses.count(), 7)
        self.assertEquals( verses[0].indicator, "1")
        self.assertEquals( verses[1].indicator, "2")
        
        # Make sure the original content
        expected_content = r"""<?xml version="1.0" ?><verse><p>*)emoi\ de\ ge/nos e)sti\n ou)k a)/shmon, a)ll' e)c i(ere/wn a)/nwqen
katabebhko/s. w(/sper d' h( par' e(ka/stois a)/llh ti/s e)stin eu)genei/as
u(po/qesis, ou(/tws par' h(mi=n h( th=s i(erwsu/nhs metousi/a tekmh/rio/n
e)stin ge/nous lampro/thtos. </p></verse>"""
        
        self.assertEquals( verses[0].original_content, expected_content)
    
    def test_load_book_alternate_state_set(self):
        
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc, state_set=1) #Using Whiston sections as opposed to the defaults
        
        chapters = Chapter.objects.filter(work=work)
        
        #print chapters[0].original_content
        
        self.assertEquals( chapters.count(), 2)
        self.assertEquals( Verse.objects.filter(chapter=chapters[0]).count(), 1)
        self.assertEquals( Verse.objects.filter(chapter=chapters[1]).count(), 1)
    
    def test_load_book_merged_state_set(self):
        
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc, state_set=None) #Using Whiston sections as opposed to the defaults
        
        chapters = Chapter.objects.filter(work=work)
        
        self.assertEquals( chapters.count(), 2)
        self.assertEquals( Verse.objects.filter(chapter=chapters[0]).count(), 6)
        self.assertEquals( Verse.objects.filter(chapter=chapters[1]).count(), 1)
    
    def test_load_book_with_sections(self):
        book_xml = self.load_test_resource('j.aj_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc, state_set=1) #Using Whiston sections as opposed to the defaults
        
        chapters = Chapter.objects.filter(work=work)
        
        self.assertEquals( chapters.count(), 1)
        #self.assertEquals( Verse.objects.filter(chapter=chapters[0]).count(), 6)

        sections = Section.objects.filter(chapters=chapters[0])
        self.assertEquals( sections.count(), 1)
        self.assertEquals( sections[0].type, "Book")
        self.assertEquals( sections[0].level, 1)
        