# -*- coding: utf8 -*-

from django.test import TestCase

from xml.dom.minidom import parse, parseString
import os

from textcritical.default_settings import SITE_ROOT
from reader.shortcuts import convert_xml_to_html5
from reader.importer.Perseus import PerseusTextImporter
from reader.importer.PerseusBatchImporter import ImportPolicy, PerseusBatchImporter, WorkDescriptor, wildcard_to_re
from reader.importer import TextImporter, LineNumber
from reader.language_tools.greek import Greek
from reader.models import Author, Division, Verse

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
            
class TestImportContext(TestCase):
        
    def test_division_level(self):
        context = TextImporter.ImportContext("TestCase")
        
        self.assertEquals( context.get_division_level_count(2), 0 )
        
        context.increment_division_level(2)
        self.assertEquals( context.get_division_level_count(2), 1 )
        
        
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
        
class TestShortcuts(TestCase):
    
    def test_process_text(self):
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>
</verse>"""

        expected_result = r"""<?xml version="1.0" encoding="utf-8"?><verse>
    <span class="head">*(ikanw=s <span class="num" data-ref="some_ref">d</span> me\n </span>
</verse>"""

        actual_result = convert_xml_to_html5(parseString(original_content), new_root_node_tag_name="verse", return_as_str=True)
        
        #self.write_out_test_file( expected_result + "\n\n" + actual_result )
        
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

        actual_result = convert_xml_to_html5( parseString(original_content), language=language, return_as_str=True)
        
        #self.write_out_test_file( expected_result + "\n\n" + actual_result )
        
        self.assertEqual(expected_result, actual_result)
        
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
        
class TestPerseusBatchImporter(TestCase):
    
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
    
    def test_import(self):
        
        dir = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test')
        
        work_descriptor = WorkDescriptor(title="Eumenides")
        
        import_policy = ImportPolicy()
        import_policy.descriptors.append( work_descriptor )
        
        importer = PerseusBatchImporter( perseus_directory=dir, book_selection_policy=import_policy.should_be_processed )
        
        self.assertEqual( importer.do_import(), 1 )
        
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
        self.importer.make_work("test_bibl_struct_import", try_to_get_existing_work=False)
        
        self.importer.import_info_from_bibl_struct(bible_struct_document)
        
        self.assertEquals(self.importer.work.authors.all()[0].name,"Flavius Josephus")
        self.assertEquals(self.importer.work.title,"Flavii Iosephi opera")
        
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
    
    def get_test_resource_file_name(self, file_name):
        return os.path.join(os.path.realpath(os.path.dirname(__file__)), 'test', file_name)
    
    def load_test_resource(self, file_name):
        
        f = None
        
        try:
            f = open( self.get_test_resource_file_name(file_name), 'r')
            return f.read()
        finally:
            if f is not None:
                f.close()
    
    def test_get_title(self):
        
        book_xml = self.load_test_resource('plut.078_teubner_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEquals( title, "Conjugalia Praecepta")
        
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
        file_name = self.get_test_resource_file_name('52_gk_portion.xml')
        self.importer.import_file(file_name)
    
    def test_load_book_no_bibl_struct(self):
        # See issue #438 (http://lukemurphey.net/issues/438)
        self.importer.state_set = 0
        file_name = self.get_test_resource_file_name('aristot.vir_gk.xml')
        self.importer.import_file(file_name)
    
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
    
    def test_load_book_alternate_state_set(self):
        self.importer.state_set = 1  #Using Whiston sections as opposed to the defaults
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        #print chapters[0].original_content
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
        
    def test_load_book_division_descriptors(self):
        self.importer.state_set = 1
        self.importer.use_line_count_for_divisions = True
        book_xml = self.load_test_resource('j.bj_gk.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        #self.assertEquals( divisions.count(), 3)
        #self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEquals( divisions[0].descriptor, "1")
        #self.assertEquals( divisions[0].descriptor, "1")
        
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
        
        #print chapters[0].original_content
        
        self.assertEquals( divisions.count(), 3)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 0)
        self.assertEquals( Verse.objects.filter(division=divisions[2]).count(), 1)
    
    def test_load_book_merged_state_set(self):
        
        self.importer.state_set = None
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEquals( divisions.count(), 2)
        self.assertEquals( Verse.objects.filter(division=divisions[0]).count(), 6)
        self.assertEquals( Verse.objects.filter(division=divisions[1]).count(), 1)
    
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
        