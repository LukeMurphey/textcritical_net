# -*- coding: utf8 -*-

from django.test import TestCase

from xml.dom.minidom import parseString
import unicodedata
import os
import sys 
from reader.shortcuts import convert_xml_to_html5
from reader.templatetags.reader_extras import perseus_xml_to_html5
from reader.importer.batch_import import ImportPolicy, WorkDescriptor, wildcard_to_re, ImportTransforms, JSONImportPolicy
from reader.importer.Perseus import PerseusTextImporter
from reader.importer.PerseusBatchImporter import PerseusBatchImporter
from reader.importer.unbound_bible import UnboundBibleTextImporter
from reader.importer import TextImporter, LineNumber
from reader.importer.Diogenes import DiogenesLemmataImporter, DiogenesAnalysesImporter
from reader.language_tools.greek import Greek
from reader import language_tools
from reader.models import Author, Division, Verse, WordDescription, WordForm, Lemma, Work
from reader.views import get_division
from reader.contentsearch import WorkIndexer, search_verses
from reader import utils

import shutil
import time

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
        
        diff_string = str( round( diff, 6) ) + " seconds"
        
        print "%s, duration=%s" % (fx.__name__, diff_string)
        
        return r
    return wrapper

class TestReader(TestCase):
    
    def get_test_resource_file_name(self, file_name):
        return os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test', file_name)
    
    def write_out_test_file(self, content):
        
        fname = '/Users/lmurphey/Desktop/output.txt'
        f = open(fname, 'w')
        f.write(content)
        f.close()
    
    def load_test_resource(self, file_name):
        
        f = None
        
        try:
            f = open( self.get_test_resource_file_name(file_name), 'r')
            return f.read()
        finally:
            if f is not None:
                f.close()

class TestGreekLanguageTools(TestReader):
    
    def test_strip_accents(self):
        self.assertEqual( language_tools.normalize_unicode( language_tools.strip_accents( u"θεός" )), u"θεος")
        
    def test_strip_accents_str(self):
        self.assertEqual( language_tools.normalize_unicode( u"θεός" ), u"θεός")
    
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
            
class TestImportContext(TestCase):
        
    def test_division_level(self):
        context = TextImporter.ImportContext("TestCase")
        
        self.assertEquals( context.get_division_level_count(2), 0 )
        
        context.increment_division_level(2)
        self.assertEquals( context.get_division_level_count(2), 1 )

class TestBatchImport(TestCase):
    
    def test_update_title_slug(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        ImportTransforms.update_title_slug(work, "english")
        
        self.assertEquals(work.title_slug, "some-doc-english")
        
    def test_update_title_slug_default(self):
        
        work = Work(title="Some Doc", language="Greek")
        work.save()
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEquals(work.title_slug, "some-doc-greek")
     
    def test_update_title_slug_by_editor(self):
        
        editor = Author(name="William Whiston")
        editor.save()
        
        work = Work(title="Some Doc", language="English")
        work.save()
        
        work.editors.add(editor)
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEquals(work.title_slug, "some-doc-whiston")

     
    def test_update_title_slug_by_editor_with_extra(self):
        
        editor = Author(name="William Whiston, Ph. D.")
        editor.save()
        
        work = Work(title="Some Doc", language="English")
        work.save()
        
        work.editors.add(editor)
        
        ImportTransforms.update_title_slug(work)
        
        self.assertEquals(work.title_slug, "some-doc-whiston")   
        
    def test_set_division_title(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            division = Division(title="Test" + str(i), sequence_number=i, work=work, level=1)
            division.save()
        
        ImportTransforms.set_division_title(work, existing_division_sequence_number=18, descriptor="NewDesc")
        
        self.assertEquals(Division.objects.get(work=work, sequence_number=18).descriptor, "NewDesc")
        
    def test_set_division_title_by_parent(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            
            parent_division = Division(title="parent" + str(i), original_title="parent" + str(i), sequence_number=i, work=work, level=1)
            parent_division.save()
            
            division = Division(title="child" + str(i), original_title="child" + str(i), sequence_number=i+100, work=work, level=2, parent_division=parent_division)
            division.save()
        
        ImportTransforms.set_division_title(work, existing_division_parent_title_slug="parent18", existing_division_title_slug="child18", descriptor="NewDesc")
        
        self.assertEquals(Division.objects.get(work=work, sequence_number=118).descriptor, "NewDesc")
        
    """
    def test_set_verse_title(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        division = Division(title="test_set_verse_title", original_title="test_set_verse_title", sequence_number=1, work=work, level=1)
        division.save()
        
        for i in range(1,5):
            verse = Verse( title=str(i), sequence_number=i, division=division)
            verse.save()
        
        ImportTransforms.set_verse_title( work, existing_verse_sequence_number=3, existing_verse_title_slug="3", descriptor="Intro")
        
        self.assertEquals(Verse.objects.get(work=work, sequence_number=3).descriptor, "Intro")
    """
    
    def test_set_division_readable(self):
        
        work = Work(title="Some Doc")
        work.save()
        
        for i in range(1,20):
            
            parent_division = Division(title=str(i), original_title=str(i), sequence_number=i, work=work, level=1, type="Book", descriptor=str(i), readable_unit=False)
            parent_division.save()
            
            division = Division(title=str(i), original_title=str(i), sequence_number=i+100, work=work, level=2, parent_division=parent_division, type="Chapter", descriptor="1", readable_unit=False)
            division.save()
        
        ImportTransforms.set_division_readable( work, sequence_number=110, title_slug="10", type="Chapter", descriptor="1", level=2)
        
        self.assertEquals(Division.objects.get(work=work, sequence_number=110).readable_unit, True)
        
class TestImport(TestCase):
     
    def setUp(self):
        self.importer = TextImporter()
        
        return super(TestImport, self).setUp()
    
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
        
class TestShortcuts(TestReader):
    
    def time_conversion (self):
        import time
        
        start = time.time()
        
        for i in range(0, 10000):
            self.test_process_text()
        
        print "Completed", time.time() - start
    
    def test_process_text(self):
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>
</verse>"""

        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><verse>
    <span class="head">*(ikanw=s <span class="num" data-ref="some_ref">d</span> me\n </span>
</verse>"""

        actual_result = convert_xml_to_html5(original_content, new_root_node_tag_name="verse", return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_text_entity(self):
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>&amp;
</verse>"""

        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><verse>
    <span class="head">*(ikanw=s <span class="num" data-ref="some_ref">d</span> me\n </span>&amp;
</verse>"""

        actual_result = convert_xml_to_html5(original_content, new_root_node_tag_name="verse", return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_custom_transformation(self):
        
        def node_transformation_fx( tag, attrs, parent, document ):
            
            if tag == "num":
                
                new_node = document.createElement( "strong" )
                
                i = 0
                for name, value in attrs:
                    
                    i = i + 1
                    new_node.setAttribute( "attr" + str(i), name + "_" + value)
                    
                return new_node
        
        original_content = r"""
<verse>
    <head>foo <num ref="some_ref">d</num> bar</head>
</verse>"""

        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><verse>
    <span class="head">foo <strong attr1="ref_some_ref">d</strong> bar</span>
</verse>"""

        actual_result = convert_xml_to_html5(original_content, new_root_node_tag_name="verse", return_as_str=True, node_transformation_fx=node_transformation_fx)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_text_with_transform(self):
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>
</verse>"""

        language = "Greek"
        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><span class="verse">
    <span class="head">Ἱκανῶς <span class="num" data-ref="some_ref">δ</span> μὲν </span>
</span>"""

        actual_result = convert_xml_to_html5(original_content, language=language, return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_text_multi_language_transforms(self):
        
        original_content = r"""<verse>koti/nois<note anchored="yes" place="unspecified" resp="ed">
                  <foreign lang="greek">koti/nois</foreign> MSS.; <foreign lang="greek">kolwnoi=s</foreign>(hills' Bekker, adopting the correction of Coraës.</note>  kai\ pa/gois</verse>""".decode("utf-8")

        language = "Greek"
        
        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><span class="verse"><span class="word">κοτίνοις</span><span class="note" data-anchored="yes" data-place="unspecified" data-resp="ed">
                  <span class="foreign" data-lang="greek"><span class="word">κοτίνοις</span></span> MSS.; <span class="foreign" data-lang="greek"><span class="word">κολωνοῖς</span></span>(hills' Bekker, adopting the correction of Coraës.</span>  <span class="word">καὶ</span> <span class="word">πάγοις</span></span>"""
        
        actual_result = perseus_xml_to_html5(original_content, language=language)
        
        # Normalize the unicode in case we have equivalent but different Unicode
        expected_result_u = unicodedata.normalize("NFC", unicode( expected_result.decode("utf-8") ) )
        actual_result_u = unicodedata.normalize("NFC", unicode( actual_result.decode("utf-8") ) )
        
        self.assertEqual( expected_result_u, actual_result_u )
        
class TestLineNumber(TestCase):
    
    def test_parse(self):
        line_number = LineNumber()
        line_number.set("354a")
        
        self.assertEquals( line_number.post, "a" )
        self.assertEquals( line_number.number, 354 )
        self.assertEquals( str(line_number), "354a" )
    
    def test_increment(self):
        line_number = LineNumber()
        line_number.set("354a")
        line_number.increment()
        
        self.assertEquals( line_number.number, 355 )
        self.assertEquals( str(line_number), "355a" )
        
    def test_copy(self):
        line_number = LineNumber()
        line_number.set("354a")
        
        new_line_number = line_number.copy()
        
        line_number.pre = "_"
        
        self.assertEquals( str(new_line_number), "354a" )
        
    def test_str(self):
        
        line_number = LineNumber()
        line_number.set("354a")
        
        self.assertEquals( str(line_number), "354a" )
        
class TestPerseusBatchImporter(TestReader):
    
    def test_wildcard(self):
        
        wc_re = wildcard_to_re("*tree*")
        
        self.assertTrue( wc_re.match("pine tree") is not None )
        self.assertTrue( wc_re.match("tree bark") is not None )
        self.assertTrue( wc_re.match("pine tree bark") is not None )
        
        self.assertTrue( wc_re.match("oak") is None )
        self.assertTrue( wc_re.match("oakland") is None )
        self.assertTrue( wc_re.match("bark") is None )
        
    def test_WorkDescriptor(self):
        
        desc = WorkDescriptor(file_name="*gk.xml")
        
        self.assertFalse( desc.rejects( desc.file_name, "/Users/Luke/Downloads/test_gk.xml" ) )
        self.assertTrue( desc.rejects( desc.file_name, "/Users/Luke/Downloads/test_eng.xml" ) )
    
    def test_match_array(self):
        
        wd = WorkDescriptor(author="Lucian", title=["Abdicatus", "Anacharsis", "Bis accusatus sive tribunalia", "Cataplus"])
        
        self.assertTrue( wd.matches( ["Abdicatus", "Anacharsis", "Bis accusatus sive tribunalia", "Cataplus"], "Anacharsis" ) )
        self.assertTrue( wd.should_be_processed("Lucian", "Anacharsis", "52.gk-xml", "Greek", None) )
        
    def test_match_editor(self):
        
        wd = WorkDescriptor(editor="Herbert Weir Smyth, Ph.D.", title="Eumenides")
        
        self.assertTrue( wd.should_be_processed("Aeschylus", "Eumenides", "52.gk-xml", "Greek", "Herbert Weir Smyth, Ph.D.") )
    
    def test_import(self):
        
        directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test')
        
        work_descriptor = WorkDescriptor(title="Eumenides")
        
        import_policy = ImportPolicy()
        import_policy.descriptors.append( work_descriptor )
        
        importer = PerseusBatchImporter( perseus_directory=directory, book_selection_policy=import_policy.should_be_processed )
        
        self.assertEqual( importer.do_import(), 1 )
        
    def test_import_editor_filter(self):
        
        directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test')
        
        work_descriptor = WorkDescriptor(title="Eumenides", editor="Herbert Weir Smyth, Ph.D.")
        
        import_policy = ImportPolicy()
        import_policy.descriptors.append( work_descriptor )
        
        importer = PerseusBatchImporter( perseus_directory=directory, book_selection_policy=import_policy.should_be_processed )
        
        self.assertEqual( importer.do_import(), 1 )
        
        
    def test_import_skip_document(self):
                
        directory = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test')
        
        # Make sure the regular descriptor matches
        work_descriptor = WorkDescriptor(author="Plutarch", title="De primo frigido", editor=["Harold Cherniss", "William C. Helmbold"])
        
        self.assertTrue( work_descriptor.should_be_processed("Plutarch", "De primo frigido", "plut.127_loeb_eng.xml", "Greek", ["Harold Cherniss", "William C. Helmbold"]) )
        
        # Make sure the dropping action matches
        work_descriptor2 = WorkDescriptor(author="Plutarch", title="De primo frigido", editor=["Harold Cherniss", "William C. Helmbold"], should_import=False )
        
        self.assertFalse( work_descriptor2.should_be_processed("Plutarch", "De primo frigido", "plut.127_loeb_eng.xml", "Greek", ["Harold Cherniss", "William C. Helmbold"]) )
        
        # Now run the imports and make sure the correct action occurs when allowing importation
        import_policy = ImportPolicy()
        import_policy.descriptors.append( work_descriptor )
        
        importer = PerseusBatchImporter( perseus_directory=directory, book_selection_policy=import_policy.should_be_processed )
        
        self.assertEqual( importer.do_import(), 1 )
        
        # Now run the imports and make sure the correct action occurs when dis-allowing importation
        import_policy2 = ImportPolicy()
        import_policy2.descriptors.append( work_descriptor2 )
        
        importer = PerseusBatchImporter( perseus_directory=directory, book_selection_policy=import_policy2.should_be_processed )
        
        self.assertEqual( importer.do_import(), 0 )
        
    def test_delete_unnecessary_divisions(self):
        
        importer = PerseusTextImporter()
        importer.state_set = 0
        importer.ignore_undeclared_divs = True
        
        book_xml = self.load_test_resource('1a_gk.xml')
        book_doc = parseString(book_xml)
        work = importer.import_xml_document(book_doc)
        
        self.assertEqual( Division.objects.filter(work=work).count(), 4)
        
        self.assertEqual( ImportTransforms.delete_unnecessary_divisions(work=work), 1)
        
        self.assertEqual( Division.objects.filter(work=work).count(), 3)
        
    def test_delete_divisions_by_title_slug(self):
        
        importer = PerseusTextImporter()
        importer.state_set = 0
        importer.ignore_undeclared_divs = True
        
        book_xml = self.load_test_resource('1a_gk.xml')
        book_doc = parseString(book_xml)
        work = importer.import_xml_document(book_doc)
        
        self.assertEqual( Division.objects.filter(work=work).count(), 4)
        
        self.assertEqual( ImportTransforms.delete_divisions_by_title_slug(work=work, title_slugs=["none"]), 1)
        
        self.assertEqual( Division.objects.filter(work=work).count(), 3)
        
class TestPerseusImport(TestReader):
    
    def setUp(self):
        self.importer = PerseusTextImporter()
    
    def test_get_title_slug(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Flavius Josephus"
        author.save()
        
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        self.assertEquals( self.importer.get_title_slug("josephi-vita"), ("josephi-vita-1" , True) )
    
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
        self.importer.make_work("test_bibl_struct_import", try_to_get_existing_work=False)
        
        self.importer.import_info_from_bibl_struct(bible_struct_document)
        
        self.assertEquals(self.importer.work.authors.all()[0].name,"Flavius Josephus")
        self.assertEquals(self.importer.work.title,"Flavii Iosephi opera")
        
    def test_findTagInDivision(self):
        
        xml = r"""<div1 type="Book" n="1">
<note anchored="yes" type="title" place="inline">*prooi/mion peri\ th=s o(/lhs pragmatei/as.
<list type="toc">
<head>*ta/de e)/nestin e)n th=| prw/th| tw=n *)iwsh/pou i(storiw=n
th=s *)ioudai+kh=s a)rxaiologi/as.</head></list></note></div1>"""

        document = parseString(xml)
        
        div_node = document.getElementsByTagName("div1")[0]
        
        head = self.importer.findTagInDivision(div_node, "head")
    
        self.assertEquals(head.tagName, "head")
        
    def test_get_language(self):
        
        language_xml = """<language id="greek">Greek</language>"""
        
        lang_document = parseString(language_xml)
        
        language = self.importer.get_language(lang_document)
        
        self.assertEquals(language, "Greek")
        
    def write_out_test_file(self, content):
        
        fname = 'C:\\Users\\Luke\\Desktop\\output.txt'
        f = open(fname, 'w')
        f.write(content)
        f.close()
        
    def test_get_text(self):
        
        sample_xml = r"<head>*ta/de e)/nestin e)n th=| <num>b</num> tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as.</head>"
        
        doc = parseString(sample_xml)
        
        head = doc.getElementsByTagName("head")[0]
        
        expected = r"*ta/de e)/nestin e)n th=|  tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as."
        
        self.assertEquals( PerseusTextImporter.getText(head.childNodes, False), expected)
        
    def test_get_text_recursive(self):
        
        sample_xml = r"<head>*ta/de e)/nestin e)n th=| <num>b</num> tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as.</head>"
        
        doc = parseString(sample_xml)
        
        head = doc.getElementsByTagName("head")[0]
        
        expected = r"*ta/de e)/nestin e)n th=| b tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as."
        
        self.assertEquals( PerseusTextImporter.getText(head.childNodes, True), expected)
        
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
    
    def test_get_title(self):
        
        book_xml = self.load_test_resource('plut.078_teubner_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEquals( title, "Conjugalia Praecepta")
        
    def test_get_title_sub_nodes(self):
        
        book_xml = self.load_test_resource('xen.socratalia_eng.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEquals( title, "Works on Socrates")
        
    def test_get_title_for_processing(self):
        
        book_xml = self.load_test_resource('xen.anab_gk_header.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEquals( title, "Anabasis")
        
    def test_get_title_not_sub(self):
        
        book_xml = self.load_test_resource('plut.gal_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEquals( title, "Galba")
        
    def test_get_author_from_tei_header(self):
        
        book_xml = self.load_test_resource('aristot.vir_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        author = PerseusTextImporter.get_author_from_tei_header(tei_header_node)
        
        self.assertEquals( author, "Aristotle")
        
    def test_get_editors(self):
        
        book_xml = self.load_test_resource('1_gk.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEquals( editors[0], "J. M. Edmonds")
        
    def test_get_editors_multiple(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEquals( editors[0], "Brooke Foss Westcott")
        self.assertEquals( editors[1], "Fenton John Anthony Hort")
        
    def test_get_editors_multiple_in_single_field(self):
        
        book_xml = self.load_test_resource('plut.127_loeb_eng.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEquals( editors[0], "Harold Cherniss")
        self.assertEquals( editors[1], "William C. Helmbold")
    
    def test_get_author_no_title_stmt(self):
        
        book_xml = self.load_test_resource('aristot.vir_gk.xml')
        book_doc = parseString(book_xml)
        self.assertEquals( PerseusTextImporter.get_author(book_doc), "Aristotle")
        
    def test_load_book_descriptorless_milestone(self):
        # See issue #440 (http://lukemurphey.net/issues/440)
        self.importer.state_set = 0
        file_name = self.get_test_resource_file_name('dh.hist04_gk.xml')
        self.importer.import_file(file_name)
        
        verse = Verse.objects.filter(division__work=self.importer.work).order_by("sequence_number")[0]
        
        self.assertEqual(verse.indicator, "1")
        
    def test_load_book_multilevel_divisions(self):
        # See issue #430 (http://lukemurphey.net/issues/430)
        self.importer.state_set = 0
        file_name = self.get_test_resource_file_name('1_gk.xml')
        self.importer.import_file(file_name)
        
        divisions = Division.objects.filter(work=self.importer.work).order_by("sequence_number")
        
        self.assertEqual(divisions[0].title, None)
        self.assertEqual(divisions[0].descriptor, u"1")
        self.assertEqual(divisions[1].title, u"Καλλίνου")
        
    def test_get_author_no_bibl_struct(self):
        
        book_xml = self.load_test_resource('plut.cat.ma_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.assertEquals( PerseusTextImporter.get_author(book_doc), "Plutarch")
        
    def test_load_bad_chars(self):
        
        book_xml = self.load_test_resource('plut.cat.ma_gk_portion.xml')
        #book_xml = self.load_test_resource('plut.cat.ma_gk.xml')
        self.importer.import_xml_string(book_xml)
        
    def test_load_bad_chars2(self):
        file_name = self.get_test_resource_file_name('plut.cat.ma_gk_portion.xml')
        self.importer.import_file(file_name)
    
    def test_load_book_with_basic_div(self):
        file_name = self.get_test_resource_file_name('52_gk.xml')
        self.importer.import_file(file_name)
        
    def test_load_book_with_milestone_line_numbers(self):
        file_name = self.get_test_resource_file_name('aesch.ag_eng.xml')
        self.importer.state_set = "*"
        self.importer.ignore_division_markers = True
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_file(file_name)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual( divisions[0].title, "lines 1-39")
        self.assertEqual( divisions[1].title, "lines 40-82")
        self.assertEqual( divisions[2].title, "lines 83-103")
        self.assertEquals( divisions[3].title, "lines 104-1616")
        self.assertEquals( divisions[4].title, "lines 1617-1648")
        self.assertEquals( divisions[5].title, "lines 1649-1672")
        
    def test_get_line_count(self):
        
        verse_xml = r"""
        <verse>
                <milestone ed="p" n="1" unit="line"/>Release from this weary task of mine has been my plea to the gods throughout this long year's watch, in which, lying upon the palace roof of the Atreidae,
                 upon my bent arm, like a dog, I have learned to know well the gathering of the night's stars, those radiant potentates conspicuous in the firmament,
                <milestone ed="p" n="5" unit="line"/>bringers of winter and summer to mankind the constellations, when they rise and set.
                <p>So now I am still watching for the signal-flame, the gleaming fire that is to bring news from <placeName key="perseus,Troy">Troy</placeName> and
                    <milestone ed="p" n="10" unit="line"/>tidings of its capture.  For thus commands my queen, woman in passionate heart and man in strength of purpose.
                      And whenever I make here my bed, restless and dank with dew and unvisited by dreams-for instead of sleep fear stands ever by my side,
                    <milestone ed="p" n="15" unit="line"/>so that I cannot close my eyelids fast in sleep-and whenever I care to sing or hum "and thus apply an antidote of song to ward off drowsiness",
                     then my tears start forth, as I bewail the fortunes of this house of ours, not ordered for the best as in days gone by.
                    <milestone ed="p" n="20" unit="line"/>But tonight may there come a happy release from my weary task!  May the fire with its glad tidings flash through the gloom!
                </p>
                <p>
                    <stage>The signal fire suddenly flashes out</stage>
                    Oh welcome, you blaze in the night, a light as if of day, you harbinger of many a choral dance in <placeName key="tgn,7010720">Argos</placeName> in thanksgiving for this glad event!
                </p>
                <p>
                    <milestone ed="p" n="25" unit="line"/>Hallo! Hallo!
                    To Agamemnon's queen I thus cry aloud the signal to rise from her bed, and as quickly as she can to lift up in her palace halls a shout of joy in welcome of this fire, if the city of <placeName key="tgn,7002329">Ilium</placeName>
                    <milestone ed="p" n="30" unit="line"/>truly is taken, as this beacon unmistakably announces.
                      And I will make an overture with a dance upon my own account; for my lord's lucky roll I shall count to my own score, now that this beacon has thrown me triple six.
                </p>
                <p>Ah well, may the master of the house come home and may
                    <milestone ed="p" n="35" unit="line"/>I clasp his welcome hand in mine!  For the rest I stay silent; a great ox stands upon my tongue
                    <note anchored="yes" n="36" resp="Smyth">A proverbial expression (of uncertain origin) for enforced silence; cf. fr. 176, 'A key stands guard upon my tongue.'</note>-
                    yet the house itself, could it but speak, might tell a plain enough tale; since, for my part, by my own choice I have words for those who know, and to those who do not know, I've lost my memory.
                </p>
        </verse>
        """
        
        verse_doc = parseString(verse_xml)
        
        line_number = self.importer.get_line_count(verse_doc)
        
        self.assertEquals( str(line_number), "35")
        
    def test_get_line_count_trailing_line(self):
        
        verse_xml = r"""
        <verse>
                <milestone ed="p" n="1" unit="line"/>Release from this weary task of mine has been my plea to the gods throughout this long year's watch, in which, lying upon the palace roof of the Atreidae,
                 upon my bent arm, like a dog, I have learned to know well the gathering of the night's stars, those radiant potentates conspicuous in the firmament,
                <milestone ed="p" n="5" unit="line"/>bringers of winter and summer to mankind the constellations, when they rise and set.
                <p>So now I am still watching for the signal-flame, the gleaming fire that is to bring news from <placeName key="perseus,Troy">Troy</placeName> and
                    <milestone ed="p" n="10" unit="line"/>tidings of its capture.  For thus commands my queen, woman in passionate heart and man in strength of purpose.
                      And whenever I make here my bed, restless and dank with dew and unvisited by dreams-for instead of sleep fear stands ever by my side,
                    <milestone ed="p" n="15" unit="line"/>so that I cannot close my eyelids fast in sleep-and whenever I care to sing or hum "and thus apply an antidote of song to ward off drowsiness",
                     then my tears start forth, as I bewail the fortunes of this house of ours, not ordered for the best as in days gone by.
                    <milestone ed="p" n="20" unit="line"/>But tonight may there come a happy release from my weary task!  May the fire with its glad tidings flash through the gloom!
                </p>
                <p>
                    <stage>The signal fire suddenly flashes out</stage>
                    Oh welcome, you blaze in the night, a light as if of day, you harbinger of many a choral dance in <placeName key="tgn,7010720">Argos</placeName> in thanksgiving for this glad event!
                </p>
                <p>
                    <milestone ed="p" n="25" unit="line"/>Hallo! Hallo!
                    To Agamemnon's queen I thus cry aloud the signal to rise from her bed, and as quickly as she can to lift up in her palace halls a shout of joy in welcome of this fire, if the city of <placeName key="tgn,7002329">Ilium</placeName>
                    <milestone ed="p" n="30" unit="line"/>truly is taken, as this beacon unmistakably announces.
                      And I will make an overture with a dance upon my own account; for my lord's lucky roll I shall count to my own score, now that this beacon has thrown me triple six.
                </p>
                <p>Ah well, may the master of the house come home and may
                    <milestone ed="p" n="35" unit="line"/>I clasp his welcome hand in mine!  For the rest I stay silent; a great ox stands upon my tongue
                    <note anchored="yes" n="36" resp="Smyth">A proverbial expression (of uncertain origin) for enforced silence; cf. fr. 176, 'A key stands guard upon my tongue.'</note>-
                    yet the house itself, could it but speak, might tell a plain enough tale; since, for my part, by my own choice I have words for those who know, and to those who do not know, I've lost my memory.
                </p>
                <p>An extra line...</p>
        </verse>
        """
        
        verse_doc = parseString(verse_xml)
        
        line_number = self.importer.get_line_count(verse_doc)
        
        self.assertEquals( str(line_number), "36")
    
    def test_load_book_with_empty_first_milestone(self):
        file_name = self.get_test_resource_file_name('52_gk.xml')
        
        self.importer.ignore_content_before_first_milestone = True
        self.importer.import_file(file_name)
        
        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division__work=self.importer.work)
        
        # This should not be:
        # ἀποκηρυχθείς τις ἰατρικὴν ἐξέμαθεν. μανέντα τὸν πατέρα καὶ ὑπὸ τῶν ἀλλων ἰατρῶν ἀπεγνωσμένον ἰασάμενος ...        
        expected = r"""<?xml version="1.0" ?><verse> ou) kaina\ me\n tau=ta, w)= a)/ndres dikastai/, ou)de\ para/doca ta\ ^ u(po\ tou= patro\s e)n tw=| paro/nti gigno/mena, ou)de\ nu=n prw=ton ta\ toiau=ta o)rgi/zetai, a)lla\ pro/xeiros ou(=tos o( no/mos au)tw=| kai\ sunh/qws e)pi\ tou=t' a)fiknei=tai to\ dikasth/rion. e)kei=no de\ kaino/teron nu=n dustuxw=, o(/ti e)/gklhma me\n i)/dion
ou)k e)/xw, kinduneu/w de\ timwri/an u(posxei=n u(pe\r th=s te/xnhs ei) mh\ pa/nta du/natai pei/qesqai tou/tw| keleu/onti, ou(= ti/ ge/noit' a)\n a)topw/teron, qerapeu/ein e)k prosta/gmatos, ou)ke/q' w(s h( te/xnh du/natai, a)ll' w(s o( path\r bou/letai ; e)boulo/mhn me\n ou)=n th\n i)atrikh\n kai\ toiou=to/n ti e)/xein
<pb id="v.5.p.478"/> fa/rmakon o(\ mh\ mo/non tou\s memhno/tas a)lla\ kai\ tou\s a)di/kws o)rgizome/nous pau/ein e)du/nato, i(/na kai\ tou=to tou= patro\s to\ no/shma i)asai/mhn. nuni\
de\ ta\ me\n th=s mani/as au)tw=| te/leon pe/pautai,
ta\ de\ th=s o)rgh=s ma=llon e)pitei/netai, kai\ to\ deino/taton, toi=s me\n a)/llois a(/pasin swfronei=, kat' e)mou= de\ tou= qerapeu/santos mo/nou mai/netai. to\n me\n ou)=n misqo\n th=s qerapei/as o(ra=te oi(=on a)polamba/nw, a)pokhrutto/menos u(p' au)tou= pa/lin kai\ tou= ge/nous a)llotriou/menos deu/teron, w(/sper dia\ tou=t' a)nalhfqei\s pro\s o)li/gon i(/n' a)timo/teros ge/nwmai polla/kis. e)kpesw\n th=s oi)ki/as.


</verse>"""
        
        self.assertEquals(verses[0].original_content, expected)
        
        self.assertEquals(divisions[1].descriptor, "1")
        self.assertEquals(divisions[1].level, 1)
    
    def test_load_book_no_bibl_struct(self):
        # See issue #438 (http://lukemurphey.net/issues/438)
        self.importer.state_set = 0
        file_name = self.get_test_resource_file_name('aristot.vir_gk.xml')
        self.importer.import_file(file_name)
    
    def test_load_book_with_line_numbers(self):
        
        book_xml = self.load_test_resource('hom.od.butler_eng.xml')
        book_doc = parseString(book_xml)
        
        #self.importer.state_set = 0
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_xml_document(book_doc)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        self.assertEquals( divisions.count(), 8)
        
        #self.assertEquals( divisions[1].title, "lines 1-32")
        self.assertEquals( divisions[0].title, "lines 1-32")
        self.assertEquals( divisions[0].title_slug, "lines-1-32")
        self.assertEquals( divisions[0].descriptor, "1")
        
    def test_load_book_with_line_numbers_per_division(self):
        
        book_xml = self.load_test_resource('hom.il.butler_eng.xml')
        book_doc = parseString(book_xml)
        
        #self.importer.state_set = 0
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_xml_document(book_doc)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        self.assertEquals( divisions.count(), 5)
        
        # Make sure that the first division has the title declared in the head node
        self.assertEquals( divisions[0].title, "Scroll 1")
        self.assertEquals( divisions[0].descriptor, "1")
        
        # Check the second division
        self.assertEquals( divisions[1].parent_division.id, divisions[0].id) # Make sure that the second is under the first node
        self.assertEquals( divisions[1].title, "lines 1-39")
        self.assertEquals( divisions[1].title_slug, "lines-1-39")
        self.assertEquals( divisions[1].descriptor, "1")
        
        # Check the third division
        self.assertEquals( divisions[2].parent_division.id, divisions[0].id)
        self.assertEquals( divisions[2].title, "lines 40-45")
        self.assertEquals( divisions[2].title_slug, "lines-40-45")
        self.assertEquals( divisions[2].descriptor, "40")
        
        # Check the fourth division
        self.assertEquals( divisions[3].parent_division, None)
        self.assertEquals( divisions[3].title, "Scroll 2")
        self.assertEquals( divisions[3].descriptor, "2")
        
        # Check the fifth division
        self.assertEquals( divisions[4].parent_division.id, divisions[3].id)
        self.assertEquals( divisions[4].title, "lines 1-15")
        self.assertEquals( divisions[4].title_slug, "lines-1-15")
        self.assertEquals( divisions[4].descriptor, "1")
        
        
        
    def test_load_book_with_line_numbers_and_parent_divisions(self):
        
        book_xml = self.load_test_resource('hom.il_eng.xml')
        book_doc = parseString(book_xml)
        
        self.importer.state_set = 0
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_xml_document(book_doc)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        self.assertEquals( str(divisions[0]), "Book 1")
        self.assertEquals( str(divisions[1]), "lines 1-32")
    
    def test_load_book(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Flavius Josephus"
        author.save()
        
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division=divisions[0])
        
        # Make sure the importer is smart enougn not to make duplicate authors
        self.assertEquals( Author.objects.filter(name="Flavius Josephus").count(), 1)
        self.assertEquals( divisions.count(), 1)
        self.assertEquals( verses.count(), 7)
        self.assertEquals( verses[0].indicator, "1")
        self.assertEquals( verses[1].indicator, "2")
        
        # Make sure we slugified the title accordingly
        self.assertEquals(self.importer.work.title_slug, "josephi-vita")
        
        # Make sure the original content
        expected_content = r"""<?xml version="1.0" ?><verse><p>*)emoi\ de\ ge/nos e)sti\n ou)k a)/shmon, a)ll' e)c i(ere/wn a)/nwqen
katabebhko/s. w(/sper d' h( par' e(ka/stois a)/llh ti/s e)stin eu)genei/as
u(po/qesis, ou(/tws par' h(mi=n h( th=s i(erwsu/nhs metousi/a tekmh/rio/n
e)stin ge/nous lampro/thtos. </p></verse>"""
        
        self.assertEquals( verses[0].original_content, expected_content)
    
    def test_load_book_division_name_from_type_field(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Flavius Josephus"
        author.save()
        
        book_xml = self.load_test_resource('07_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)[:1]
        
        # Make sure the division title was set correctly
        self.assertEquals( divisions[0].title, "Introduction")
        self.assertEquals( divisions[0].original_title, "intro")
    
    def test_load_book_multiple_texts(self):
        """
        Make sure works that include multiple text nodes are imported correctly,
        
        See #459, http://lukemurphey.net/issues/459
        """
        
        # This work has multiple text nodes. See if they are imported as separate units
        self.importer.state_set = 0
        book_xml = self.load_test_resource('apollod_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division__work=self.importer.work)
        
        # Make sure no divisions are marked readable if they have no verses
        for division in divisions:
            if division.readable_unit:
                self.assertGreater( Verse.objects.filter(division=division).count(), 0)
        
        self.assertEquals( divisions[0].descriptor, "Library")
        
        # 35: 28 sections + 2 text nodes + 3 chapters + 2 div1
        self.assertEquals( divisions.count(), 35)
        self.assertEquals( verses.count(), 28)
        
    def test_load_book_texts_with_head(self):
        
        # This work has multiple text nodes. See if they are imported as separate units
        self.importer.state_set = 0
        book_xml = self.load_test_resource('appian.fw_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division__work=self.importer.work)
        
        self.assertEquals( divisions[0].descriptor, "Reg.")
        self.assertEquals( divisions[0].original_title, "*e*k *t*h*s *b*a*s*i*l*i*k*h*s.")
        
        # 2: 1 text nodes, 0 chapters, 1 div1
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( verses.count(), 2)
    
    def test_load_book_editors(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Fenton John Anthony Hort"
        author.save()
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        self.assertEquals( Author.objects.filter(name="Fenton John Anthony Hort").count(), 1)
        
        self.assertEquals( self.importer.work.editors.all().count(), 2 )
        self.assertEquals( self.importer.work.editors.filter(name="Brooke Foss Westcott").count(), 1 )
        self.assertEquals( self.importer.work.editors.filter(name="Fenton John Anthony Hort").count(), 1 )
    
    def test_load_book_alternate_state_set(self):
        self.importer.state_set = 1  #Using Whiston sections as opposed to the defaults
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
        
    def test_load_book_division_descriptors(self):
        self.importer.state_set = 1
        book_xml = self.load_test_resource('j.bj_gk.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( divisions[0].descriptor, "1")
        
    def test_load_book_line_count_division_titles(self):
        self.importer.state_set = 1
        self.importer.use_line_count_for_divisions = True
        book_xml = self.load_test_resource('aesch.eum_gk.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        #self.assertEquals( divisions.count(), 3)
        #self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEquals( divisions[1].title, "lines 1-33")
        self.assertEquals( divisions[2].title, "lines 34-38")
        
    def test_load_book_empty_sub_divisions(self):
        self.importer.state_set = 0
        
        book_xml = self.load_test_resource('aesch.lib_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 6) # Was 3 before cards are always treated as chunks
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
        self.assertEquals( Verse.objects.filter(division=divisions[2]).count(), 0)
    
    def test_load_book_no_chunks(self):
        # See bug #446, http://lukemurphey.net/issues/446
        self.importer.state_set = 0
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions[0].original_title, "*k*a*t*a *m*a*q*q*a*i*o*n")
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 4)
        
    def test_load_book_xml_processing_instruction(self):
        # See bug #557, http://lukemurphey.net/issues/557
        self.importer.state_set = 0
        
        book_xml = self.load_test_resource('hist_eng.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
    def test_load_book_no_verses(self):
        # See bug #446, http://lukemurphey.net/issues/446
        self.importer.state_set = "*"
        
        book_xml = self.load_test_resource('char_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions[0].original_title, "*Prooi/mion")
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 5)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 5)
        
    def test_load_book_no_verses2(self):
        # See bug #446, http://lukemurphey.net/issues/446
        self.importer.state_set = 0
        self.importer.ignore_division_markers = False
        
        book_xml = self.load_test_resource('plut.068_teubner_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
    
    def test_load_book_merged_state_set(self):
        
        self.importer.state_set = None
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 6)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
    
    def test_load_book_ignore_divs_not_in_refsdecl(self):
        
        self.importer.state_set = 0
        self.importer.ignore_undeclared_divs = True
        file_name = self.get_test_resource_file_name('1_gk.xml')
        self.importer.import_file(file_name)
        
        divisions = Division.objects.filter( work=self.importer.work )
        
        # Make sure that the div3 nodes were not treated as chunks
        self.assertEquals(len(divisions), 3) # Would be 5 otherwise
        
    
    def test_load_book_with_sections(self):
        
        self.importer.state_set = 1 #Using Whiston sections as opposed to the defaults
        book_xml = self.load_test_resource('j.aj_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work).distinct()
        
        self.assertEquals( divisions[1].descriptor, "pr.")
        self.assertEquals( Verse.objects.filter(division__work=work).count(), 5)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 2)
        
        self.assertEquals( divisions.count(), 5)
        self.assertEquals( divisions[0].type, "Book")
        self.assertEquals( divisions[0].level, 1)
        
        self.assertEquals( divisions[1].type, "Whiston chapter")
        self.assertEquals( divisions[1].level, 2)
        
        self.assertEquals( divisions[0].original_title, r"""*ta/de e)/nestin e)n th=| prw/th| tw=n *)iwsh/pou i(storiw=n
th=s *)ioudai+kh=s a)rxaiologi/as.""" )
        self.assertEquals( divisions[2].original_title, r"""*ta/de e)/nestin e)n th=| b tw=n *)iwsh/pou i(storiw=n th=s
*)ioudai+kh=s a)rxaiologi/as.""" )
        
        # Make sure that the text from the TOC did not get included
        expected_content = r"""<?xml version="1.0" ?><verse><milestone n="1" unit="section"/><p>*meta\ de\ th\n *)isa/kou teleuth\n oi( pai=des au)tou= merisa/menoi 
th\n oi)/khsin pro\s a)llh/lous ou)x h(\n e)/labon tau/thn kate/sxon,
a)ll' *(hsau=s me\n th=s *nebrwni/as po/lews e)kxwrh/sas tw=| a)delfw=| e)n
*saeira=| dihta=to kai\ th=s *)idoumai/as h)=rxen ou(/tw kale/sas th\n xw/ran
a)p' au)tou=: *)/adwmos ga\r e)pwnoma/zeto kata\ toiau/thn ai)ti/an tuxw\n
th=s e)piklh/sews. <milestone n="2" unit="section"/>a)po\ qh/ras pote\ kai\ po/nou tou= peri\ to\ kunh/gion 
limw/ttwn e)panh=ken, e)/ti de\ h)=n pai=s th\n h(liki/an, e)pituxw\n
de\ ta)delfw=| fakh=n e)skeuako/ti pro\s a)/riston au(tw=| canqh\n sfo/dra
th\n xroia\n kai\ dia\ tou=t' e)/ti ma=llon o)rexqei\s h)ci/ou parasxei=n
au)tw=| pro\s trofh/n. <milestone n="3" unit="section"/>o( de\ a)podo/sqai to\ presbei=on au)tw=| tou= fagei=n
sunergw=| xrhsa/menos th=| pei/nh| to\n a)delfo\n h)na/gkaze, ka)kei=nos u(po\
tou= limou= proaxqei\s paraxwrei= tw=n presbei/wn au)tw=| meq' o(/rkwn.
e)/nqen dia\ th\n canqo/thta tou= brw/matos u(po\ tw=n h(likiwtw=n kata\
paidia\n *)/adwmos e)piklhqei/s, a)/dwma ga\r *(ebrai=oi to\ e)ruqro\n kalou=si, 
th\n xw/ran ou(/tws proshgo/reusen: *(/ellhnes ga\r au)th\n e)pi\ to\
semno/teron *)idoumai/an w)no/masan.
</p></verse>"""
        
        self.assertEquals( Verse.objects.filter(division=divisions[3])[0].original_content, expected_content)
        
    
    def test_load_book_break_sections(self):
        # See #424, http://lukemurphey.net/issues/424
        
        book_xml = self.load_test_resource('aristd.rhet_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_last_state_is_non_chunk = True
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEquals(divisions.count(), 5)
        self.assertEquals(divisions[1].parent_division.id, divisions[0].id)
        self.assertEquals(divisions[2].parent_division.id, divisions[1].id)
        
        self.assertEquals(divisions[4].parent_division.id, divisions[3].id)
        
    def test_load_book_ignore_divs_and_use_line_numbers(self):
        # See #468, http://lukemurphey.net/issues/468
        
        book_xml = self.load_test_resource('soph.trach_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.use_line_count_for_divisions = True
        self.importer.ignore_division_markers = True
        self.importer.state_set = 0
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEquals(divisions.count(), 4)
        self.assertEquals(divisions[0].title, "lines 1-48")
        
    def test_load_book_only_bottom_division_readable(self):
        # See #502, http://lukemurphey.net/issues/502
        
        book_xml = self.load_test_resource('01_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_leaf_divisions_readable = True
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEquals(divisions.count(), 13)
        self.assertEquals(divisions.filter(readable_unit=True).count(), 11) #is 13 without using only_leaf_divisions_readable = True 
        
    def test_load_book_explicit_division_tags(self):
        # See #503, http://lukemurphey.net/issues/503
        
        book_xml = self.load_test_resource('01_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_leaf_divisions_readable = True
        self.importer.division_tags = ["div1", "div2"]
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEquals(divisions.count(), 12) #Should not have made the div3 under chapter 10 a division
        
    def test_xml_use_line_numbers(self):
        
        tei_node_portion_xml = """
        <teiHeader type="text" status="new">
            <encodingDesc>
                <refsDecl doctype="TEI.2">
                <step refunit="line" from="DESCENDANT (1 L N%1)"/>
                </refsDecl>
                <refsDecl doctype="TEI.2">
                <state unit="card"/>
                </refsDecl>
            </encodingDesc>
        </teiHeader>
        """
        
        tei_node_portion_doc = parseString( tei_node_portion_xml )
        
        self.assertTrue( PerseusTextImporter.use_line_numbers_for_division_titles(tei_node_portion_doc) )
        
        
    def test_xml_dont_use_line_numbers(self):
        
        tei_node_portion_xml = """
        <teiHeader type="text" status="new">
            <encodingDesc>
                <refsDecl doctype="TEI.2">
                <state unit="card"/>
                </refsDecl>
            </encodingDesc>
        </teiHeader>
        """
        
        tei_node_portion_doc = parseString( tei_node_portion_xml )
        
        self.assertFalse( PerseusTextImporter.use_line_numbers_for_division_titles(tei_node_portion_doc) )
        
    def test_line_count_update(self):
        
        verse_xml = """
        <verse>
            <l>One</l>
            <l>Two</l>
            <l>Three</l>
            <l>Four</l>
        </verse>
        """
        
        verse_doc = parseString( verse_xml )
        
        line_count = PerseusTextImporter.get_line_count(verse_doc)
        
        self.assertEquals( str(line_count), "4")
        
    def test_line_count_update_with_start(self):
        
        verse_xml = """
        <verse>
            <l>Six</l>
            <l>Seven</l>
            <l>Eight</l>
            <l>Nine</l>
        </verse>
        """
        
        verse_doc = parseString( verse_xml)
        
        line_count = PerseusTextImporter.get_line_count(verse_doc, count = 5)
        
        self.assertEquals( str(line_count), "9")
        
    def test_line_count_update_with_specifier(self):
        
        verse_xml = """
        <verse>
            <l>Six</l>
            <l n="7">Seven</l>
            <l>Eight</l>
            <l>Nine</l>
        </verse>
        """
        
        verse_doc = parseString( verse_xml)
        
        line_count = PerseusTextImporter.get_line_count(verse_doc)
        
        self.assertEquals( str(line_count), "9")
        
class TestDivisionModel(TestReader):
    
    def setUp(self):
        self.importer = PerseusTextImporter()
    
    def test_get_division_indicators(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')        
        self.importer.import_xml_string(book_xml)
        
        division = Division.objects.filter(work=self.importer.work)[1]
        
        self.assertEquals( division.get_division_indicators(), [u'Matthew', u'1'] )
        
    def test_get_division_description(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')        
        self.importer.import_xml_string(book_xml)
        
        # Build a description
        division = Division.objects.filter(work=self.importer.work)[1]
        self.assertEquals( division.get_division_description(), "Matthew 1" )
        
        # Build a description using the titles
        division = Division.objects.filter(work=self.importer.work)[1]
        self.assertEquals( division.get_division_description(use_titles=True), "ΚΑΤΑ ΜΑΘΘΑΙΟΝ chapter 1" )
        
        # Build a description with a verse
        verse = Verse.objects.filter(division=division).order_by("sequence_number")[0]
        self.assertEquals( division.get_division_description(verse=verse), "Matthew 1:1" )
        
class TestViews(TestReader):
    
    def test_get_division(self):
        
        importer = PerseusTextImporter()
        book_xml = self.load_test_resource('nt_gk.xml')
        work = importer.import_xml_string(book_xml)
        
        division = get_division( work, 'Matthew', '1')
        
        self.assertEquals( division.descriptor, '1' )
        self.assertEquals( division.parent_division.descriptor, 'Matthew' )
                
class TestDiogenesLemmaImport(TestReader):    
    
    def make_lemma(self):
        lemma = Lemma(lexical_form=Greek.beta_code_str_to_unicode("a(/bra"), language="Greek", reference_number=537850)
        lemma.save()
        
        return lemma
    
    def make_form(self):
        
        lemma = self.make_lemma()
        
        word_form = WordForm()
        word_form.lemma = lemma
        word_form.form = Greek.beta_code_str_to_unicode("a(/bra")
        word_form.save()
        
        return word_form
    
    @time_function_call
    def test_import_file(self):
        
        lemmas = DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        self.assertEquals( len(lemmas), 95)
    
    def test_parse(self):
        
        f = open( self.get_test_resource_file_name("greek-lemmata.txt"), 'r')
        s = f.readline()
        
        lemma = DiogenesLemmataImporter.parse_lemma(s)
        
        self.assertEquals(lemma.lexical_form, Greek.beta_code_str_to_unicode("a(/bra"))
        self.assertEquals(lemma.reference_number, 537850)

class TestReaderUtils(TestReader):
    
    @time_function_call
    def test_get_word_descriptions(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        descriptions = utils.get_word_descriptions(u"ἅβρυνα", False)
        
        self.assertEquals( len(descriptions), 2 )
        
    @time_function_call
    def test_get_all_related_forms(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        forms = utils.get_all_related_forms(u"ἅβραν", False) #a(/bran
        
        self.assertEquals( len(forms), 6 )
        
    @time_function_call
    def test_get_all_related_forms_no_diacritics(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        forms = utils.get_all_related_forms(u"αβραν", True) #a(/bran
        
        self.assertEquals( len(forms), 6 ) 

class TestDiogenesAnalysesImport(TestReader):
    
    @time_function_call
    def test_import_file(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        # See if the analyses match up with the lemmas
        # Find the word description and make sure the lemma matches
        descriptions = WordDescription.objects.filter(meaning="favourite slave" )
        
        self.assertEqual(descriptions[0].lemma.reference_number, 537850)
        self.assertEqual(descriptions[0].meaning, "favourite slave")
        
    def test_import_file_no_match(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata-no-match.txt"), return_created_objects=True)
        
        # Import the analyses
        analyses = DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses-no-match.txt"), return_created_objects=True, raise_exception_on_match_failure=True)
        
        self.assertEqual(len(analyses), 4)
        
    @time_function_call
    def test_lookup_by_form(self):
        
        # Get the lemmas so that we can match up the 
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        # Import the analyses
        DiogenesAnalysesImporter.import_file(self.get_test_resource_file_name("greek-analyses2.txt"), return_created_objects=True)
        
        # See if the analyses match up with the lemmas
        # Find the word description and make sure the lemma matches
        
        descriptions = WordDescription.objects.filter(word_form__form=Greek.beta_code_str_to_unicode("a(/bra") )
        
        self.assertEqual(descriptions[0].lemma.reference_number, 537850)
        self.assertEqual(descriptions[0].meaning, "favourite slave")
        
        
    def make_lemma(self):
        lemma = Lemma(lexical_form=Greek.beta_code_str_to_unicode("a(/bra"), language="Greek", reference_number=537850)
        lemma.save()
        
        return lemma
    
    def make_form(self):
        
        lemma = self.make_lemma()
        
        word_form = WordForm()
        word_form.lemma = lemma
        word_form.form = Greek.beta_code_str_to_unicode("a(/bra")
        word_form.save()
        
        return word_form
        
    def test_handle_multiple_genders(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata.txt"), return_created_objects=True)
        
        word_form = self.make_form()
        
        description = DiogenesAnalysesImporter.import_analysis_entry("537850 9 a_)ghko/ti,a)ga/w\t \tperf part act masc/neut dat sg (attic doric ionic aeolic)}" , word_form)
        
        self.assertTrue( description.masculine )
        self.assertTrue( description.neuter )
        self.assertFalse( description.feminine )
        
    def test_handle_no_match(self):
        
        # Get the lemmas so that we can match up the analyses
        DiogenesLemmataImporter.import_file(self.get_test_resource_file_name("greek-lemmata-no-match.txt"), return_created_objects=True)
        
        word_form = self.make_form()
        
        #full_entry = "e)pamfie/sasqai\t{31475848 9 e)pamfi+e/sasqai,e)pi/,a)mfi/-e(/zomai\tseat oneself\taor inf mid (attic epic doric ionic aeolic parad_form prose)}[40532015][6238652]{6264700 9 e)pi/-a)mfia/zw\tciothe\taor inf mid}[40532015]{6365952 9 e)pi/-a)mfie/nnumi\tput round\taor inf mid (attic)}[40532015]"
        
        word_description = DiogenesAnalysesImporter.import_analysis_entry( "e)pamfie/sasqai\t{31475848 9 e)pamfi+e/sasqai,e)pi/,a)mfi/-e(/zomai\tseat oneself\taor inf mid (attic epic doric ionic aeolic parad_form prose)}[40532015][6238652]", word_form)
        
        self.assertNotEqual(word_description, None)
        
    def test_parse_no_match(self):
        
        word_form = WordForm()
        word_form.form = unicode("test_parse_no_match", "UTF-8")
        word_form.save()
        
        desc = "Wont match regex"
        
        # Make sure this does not trigger an exception
        self.assertEquals( DiogenesAnalysesImporter.import_analysis_entry(desc, word_form), None )
    
    
class TestWorkIndexer(WorkIndexer):
    
    @classmethod
    def get_index_dir(cls):
        return os.path.join("..", "var", "tests", "indexes")
    
    @classmethod
    def delete_index(cls):
        shutil.rmtree( cls.get_index_dir(), ignore_errors=True )
    
class TestContentSearch(TestReader):
    
    indexer = None
    
    def setUp(self):
        
        self.indexer = TestWorkIndexer
        
        # Remove any existing index files from previous tests
        self.indexer.delete_index()

    def make_work(self, content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.", division_title="test_add_doc(division)", work_title="test_add_doc", work_title_slug=None, division_title_slug=None, division_descriptor=None):
        author = Author()
        author.name = "Luke"
        author.save()
        
        work = Work(title=work_title)
        
        if work_title_slug:
            work.title_slug = work_title_slug
        
        work.save()
        
        division = Division(work=work, title=division_title, readable_unit=True, level=1, sequence_number=1)
        
        if division_title_slug:
            division.title_slug = division_title_slug
            
        if division_descriptor:
            division.descriptor = division_descriptor
        
        division.save()
        
        verse = Verse(division=division, indicator="1", sequence_number=1, content=content)
        verse.save()
        
        return verse, division, work
    
    def tearDown(self):
        
        # Remove the index files so they don't cause problems with future tests
        self.indexer.delete_index()
    
    def test_index_verse(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( "amet", self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
        
    def test_search_verse_no_diacritic(self):
        
        # Make a work
        verse, division, work = self.make_work(u"ἐξ ἔργων νόμου οὐ δικαιωθήσεται πᾶσα σὰρξ")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( u"no_diacritics:νομου", self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
        
    def test_search_verse_beta_code(self):
        
        # Make a work
        verse, division, work = self.make_work( u"ἐξ ἔργων νόμου οὐ δικαιωθήσεται πᾶσα σὰρξ" )
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( u'NO/MOU', self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
        
    def test_search_verse_beta_code_no_diacritics(self):
        
        # Make a work
        verse, division, work = self.make_work(u"ἐξ ἔργων νομου οὐ δικαιωθήσεται πᾶσα σὰρξ")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( u"NOMOU", self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
    
    def test_search_verse_work_by_slug(self):
        
        # Make a work
        verse, division, work = self.make_work(work_title="New Testament", work_title_slug=u"test_search_verse_work_by_slug")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( u"work_id:test_search_verse_work_by_slug", self.indexer.get_index() )
        self.assertEquals( len(results.verses), 1 )
        
        results = search_verses( u"work:test_search_verse_work_by_slug", self.indexer.get_index() )
        self.assertEquals( len(results.verses), 1 )

        results = search_verses( u'work:"New Testament"', self.indexer.get_index() )
        self.assertEquals( len(results.verses), 1 )        
        
    def test_search_division_by_slug(self):
        
        # Make a work
        verse, division, work = self.make_work(division_title="Some Division", division_descriptor=u"division_descriptor")
        
        self.indexer.get_index(create=True)
        self.indexer.index_verse(verse, commit=True)
        
        results = search_verses( u"section:division_descriptor", self.indexer.get_index() )
        self.assertEquals( len(results.verses), 1 )

        results = search_verses( u'section:"Some Division"', self.indexer.get_index() )
        self.assertEquals( len(results.verses), 1 )        
        
        
    def test_index_work(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_work(work)
        
        results = search_verses( "amet", self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
        
    def test_index_division(self):
        
        # Make a work
        verse, division, work = self.make_work()
        
        self.indexer.get_index(create=True)
        self.indexer.index_division(division)
        
        results = search_verses( "amet", self.indexer.get_index() )
        
        self.assertEquals( len(results.verses), 1 )
        
class TestUnboundBibleImport(TestReader):
    
    def setUp(self):
        self.importer = UnboundBibleTextImporter()
        
    def test_import_file(self):
        
        work = Work(title="LXX (Septuagint)", title_slug="lxx")
        work.save()
        
        self.importer.work = work
        
        self.importer.import_file( self.get_test_resource_file_name("lxx_a_accents_utf8.txt") )
        
        genesis   = Division.objects.filter(work=work)[0]
        chapter_1 = Division.objects.filter(work=work)[1]
        chapter_2 = Division.objects.filter(work=work)[2]
        chapter_3 = Division.objects.filter(work=work)[3]
        
        self.assertEquals( Division.objects.filter(work=work).count(), 4)
        
        self.assertEquals( Verse.objects.count(), 65)
        
        self.assertEquals( Verse.objects.filter(indicator="1")[0].content, language_tools.normalize_unicode(u"ἐν ἀρχῇ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν") )
        self.assertEquals( Verse.objects.filter(division=chapter_1).count(), 31)
        self.assertEquals( Verse.objects.filter(division=chapter_2).count(), 25)
        self.assertEquals( Verse.objects.filter(division=chapter_3).count(), 9)
        
        self.assertEquals( genesis.title, "Genesis" )
        self.assertEquals( genesis.title_slug, "genesis" )
        
        # Make sure the sequence numbers increase
        num = 0
        
        for book in Division.objects.filter(readable_unit=False).order_by('sequence_number'):
            num = num + 1
            self.assertEquals( book.sequence_number, num, str(book) + " does not have the expected sequence number (%i versus expected %i)" % (book.sequence_number, num) )
            
            for chapter in Division.objects.filter(parent_division=book).order_by('sequence_number'):
                num = num + 1
                self.assertEquals( chapter.sequence_number, num, str(chapter) + " does not have the expected sequence number (%i versus expected %i)" % (chapter.sequence_number, num) )
        
    def test_import_file_work_not_precreated(self):
        
        self.importer.import_file( self.get_test_resource_file_name("lxx_a_accents_utf8.txt") )
        
        self.assertEquals( self.importer.work.title, "Greek OT: LXX")
        
    def test_import_file_with_policy(self):
        
        import_policy_file = os.path.join( os.path.split(sys.argv[0])[0], "reader", "importer", "unbound_bible_import_policy.json")
        
        import_policy = JSONImportPolicy()
        import_policy.load_policy( import_policy_file )
        
        self.importer.import_policy = import_policy.should_be_processed
        self.importer.import_file( self.get_test_resource_file_name("lxx_a_accents_utf8.txt") )
        
        self.assertEquals( self.importer.work.title, "Septuagint (LXX)")
        self.assertEquals( self.importer.work.language, "Greek")
        
    def test_load_book_names(self):
        
        book_names = self.importer.load_book_names( self.get_test_resource_file_name("book_names.txt") )
        
        self.assertEquals(book_names["01O"], "Genesis")
        
    def test_find_and_load_book_names_same_dir(self):
        
        book_names = self.importer.find_and_load_book_names( self.get_test_resource_file_name("lxx_a_accents_utf8.txt") )
        
        self.assertEquals(book_names["01O"], "Genesis")
        
    def test_find_and_load_book_names_constructor_arg(self):
        
        self.importer = UnboundBibleTextImporter(book_names_file=self.get_test_resource_file_name("book_names.txt") )
        
        book_names = self.importer.find_and_load_book_names()
        
        self.assertEquals(book_names["01O"], "Genesis")
        
    def test_get_name_from_comment(self):
        
        name = self.importer.get_name_from_comment("#name\tGreek NT: Westcott/Hort, UBS4 variants")
        
        self.assertEquals( name, "Greek NT: Westcott/Hort, UBS4 variants")
        
    def test_get_name_from_comment_truncated(self):
        
        name = self.importer.get_name_from_comment("#name\tGreek OT: LXX [A] Accented")
        
        self.assertEquals( name, "Greek OT: LXX")