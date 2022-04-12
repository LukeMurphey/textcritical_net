from xml.dom.minidom import parseString
from . import TestReader
from reader.importer.Perseus import PerseusTextImporter
from reader.models import Author, Division, Verse, WordDescription, WordForm, Lemma, Work, WorkAlias, WikiArticle

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
        
        self.assertEqual(self.importer.get_title_slug("josephi-vita"), ("josephi-vita-1" , True))
    
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
        
        self.assertEqual(self.importer.work.authors.all()[0].name,"Flavius Josephus")
        self.assertEqual(self.importer.work.title,"Flavii Iosephi opera")
        
    def test_findTagInDivision(self):
        
        xml = r"""<div1 type="Book" n="1">
<note anchored="yes" type="title" place="inline">*prooi/mion peri\ th=s o(/lhs pragmatei/as.
<list type="toc">
<head>*ta/de e)/nestin e)n th=| prw/th| tw=n *)iwsh/pou i(storiw=n
th=s *)ioudai+kh=s a)rxaiologi/as.</head></list></note></div1>"""

        document = parseString(xml)
        
        div_node = document.getElementsByTagName("div1")[0]
        
        head = self.importer.findTagInDivision(div_node, "head")
    
        self.assertEqual(head.tagName, "head")
        
    def test_get_language(self):
        
        language_xml = """<language id="greek">Greek</language>"""
        
        lang_document = parseString(language_xml)
        
        language = self.importer.get_language(lang_document)
        
        self.assertEqual(language, "Greek")
        
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
        
        self.assertEqual(PerseusTextImporter.getText(head.childNodes, False), expected)
        
    def test_get_text_recursive(self):
        
        sample_xml = r"<head>*ta/de e)/nestin e)n th=| <num>b</num> tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as.</head>"
        
        doc = parseString(sample_xml)
        
        head = doc.getElementsByTagName("head")[0]
        
        expected = r"*ta/de e)/nestin e)n th=| b tw=n *)iwsh/pou i(storiw=n th=s *)ioudai+kh=s a)rxaiologi/as."
        
        self.assertEqual(PerseusTextImporter.getText(head.childNodes, True), expected)
        
    def test_get_states(self):
                                    
        states_xml = """ <refsDecl doctype="TEI.2">
                            <state unit="section"/>
                            <state n="chunk" unit="Whiston section"/>
                         </refsDecl>"""
                            
        states_doc = parseString(states_xml)
        
        states = PerseusTextImporter.getStates(states_doc)
        
        self.assertEqual(states[0].name, "section")
        self.assertEqual(states[1].name, "Whiston section")
        self.assertEqual(states[1].section_type, "chunk")
        
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
        
        self.assertEqual(chunks[0][0].name, "section")
        
        self.assertEqual(chunks[1][0].name, "Whiston section")
        self.assertEqual(chunks[1][0].section_type, "chunk")
    
    def test_get_title(self):
        
        book_xml = self.load_test_resource('plut.078_teubner_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEqual(title, "Conjugalia Praecepta")
        
    def test_get_title_sub_nodes(self):
        
        book_xml = self.load_test_resource('xen.socratalia_eng.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEqual(title, "Works on Socrates")
        
    def test_get_title_for_processing(self):
        
        book_xml = self.load_test_resource('xen.anab_gk_header.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEqual(title, "Anabasis")
        
    def test_get_title_not_sub(self):
        
        book_xml = self.load_test_resource('plut.gal_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        title = PerseusTextImporter.get_title_from_tei_header(tei_header_node)
        
        self.assertEqual(title, "Galba")
        
    def test_get_author_from_tei_header(self):
        
        book_xml = self.load_test_resource('aristot.vir_gk.xml')
        book_doc = parseString(book_xml)
        
        tei_header_node = book_doc.getElementsByTagName("teiHeader")[0]
        
        author = PerseusTextImporter.get_author_from_tei_header(tei_header_node)
        
        self.assertEqual(author, "Aristotle")
        
    def test_get_editors(self):
        
        book_xml = self.load_test_resource('1_gk.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEqual(editors[0], "J. M. Edmonds")
        
    def test_get_editors_multiple(self):
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEqual(editors[0], "Brooke Foss Westcott")
        self.assertEqual(editors[1], "Fenton John Anthony Hort")
        
    def test_get_editors_multiple_in_single_field(self):
        
        book_xml = self.load_test_resource('plut.127_loeb_eng.xml')
        book_doc = parseString(book_xml)
        
        editors = PerseusTextImporter.get_editors(book_doc)
        
        self.assertEqual(editors[0], "Harold Cherniss")
        self.assertEqual(editors[1], "William C. Helmbold")
    
    def test_get_author_no_title_stmt(self):
        
        book_xml = self.load_test_resource('aristot.vir_gk.xml')
        book_doc = parseString(book_xml)
        self.assertEqual(PerseusTextImporter.get_author(book_doc), "Aristotle")
        
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
        self.assertEqual(divisions[0].descriptor, "1")
        self.assertEqual(divisions[1].title, "Καλλίνου")
        
    def test_get_author_no_bibl_struct(self):
        
        book_xml = self.load_test_resource('plut.cat.ma_gk_portion.xml')
        book_doc = parseString(book_xml)
        self.assertEqual(PerseusTextImporter.get_author(book_doc), "Plutarch")
        
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
        
        self.assertEqual(divisions[0].title, "lines 1-39")
        self.assertEqual(divisions[1].title, "lines 40-82")
        self.assertEqual(divisions[2].title, "lines 83-103")
        self.assertEqual(divisions[3].title, "lines 104-1616")
        self.assertEqual(divisions[4].title, "lines 1617-1648")
        self.assertEqual(divisions[5].title, "lines 1649-1672")

    def test_load_book_with_multiple_divisions_with_same_id(self):
        # See https://lukemurphey.net/issues/2537
        # This checks the logic that 
        file_name = self.get_test_resource_file_name('overriding_div.xml')
        self.importer.state_set = "*"
        self.importer.ignore_division_markers = False
        
        self.importer.import_file(file_name)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions[1].descriptor, "1")
        self.assertEqual(divisions[2].descriptor, "2")
        # self.assertEqual(divisions[3].descriptor, "2a")
        
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
        
        line_number, _ = self.importer.get_line_count(verse_doc)
        
        self.assertEqual(str(line_number), "35")
        
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
        
        line_number, _ = self.importer.get_line_count(verse_doc)
        
        self.assertEqual(str(line_number), "36")
    
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
        
        self.assertEqual(verses[0].original_content, expected)
        
        self.assertEqual(divisions[1].descriptor, "1")
        self.assertEqual(divisions[1].level, 1)
    
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
        
        self.assertEqual(divisions.count(), 10)
        
        #self.assertEqual(divisions[1].title, "lines 1-32")
        
        self.assertEqual(divisions[1].title, "lines 1-96")
        self.assertEqual(divisions[1].title_slug, "lines-1-96")
        self.assertEqual(divisions[1].descriptor, "1")
        
        
        self.assertEqual(divisions[8].title, "Scroll 2")
        self.assertEqual(divisions[8].descriptor, "2")
        
        self.assertEqual(divisions[9].title, "lines 1-15")
        self.assertEqual(divisions[9].title_slug, "lines-1-15")
        self.assertEqual(divisions[9].descriptor, "1")
        
    def test_load_book_with_line_numbers_per_division(self):
        
        book_xml = self.load_test_resource('hom.il.butler_eng.xml')
        book_doc = parseString(book_xml)
        
        #self.importer.state_set = 0
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_xml_document(book_doc)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        self.assertEqual(divisions.count(), 5)
        
        # Make sure that the first division has the title declared in the head node
        self.assertEqual(divisions[0].title, "Scroll 1")
        self.assertEqual(divisions[0].descriptor, "1")
        
        # Check the second division
        self.assertEqual(divisions[1].parent_division.id, divisions[0].id) # Make sure that the second is under the first node
        self.assertEqual(divisions[1].title, "lines 1-39")
        self.assertEqual(divisions[1].title_slug, "lines-1-39")
        self.assertEqual(divisions[1].descriptor, "1")
        
        # Check the third division
        self.assertEqual(divisions[2].parent_division.id, divisions[0].id)
        self.assertEqual(divisions[2].title, "lines 40-45")
        self.assertEqual(divisions[2].title_slug, "lines-40-45")
        self.assertEqual(divisions[2].descriptor, "40")
        
        # Check the fourth division
        self.assertEqual(divisions[3].parent_division, None)
        self.assertEqual(divisions[3].title, "Scroll 2")
        self.assertEqual(divisions[3].descriptor, "2")
        
        # Check the fifth division
        self.assertEqual(divisions[4].parent_division.id, divisions[3].id)
        self.assertEqual(divisions[4].title, "lines 1-15")
        self.assertEqual(divisions[4].title_slug, "lines-1-15")
        self.assertEqual(divisions[4].descriptor, "1")
        
        
        
    def test_load_book_with_line_numbers_and_parent_divisions(self):
        
        book_xml = self.load_test_resource('hom.il_eng.xml')
        book_doc = parseString(book_xml)
        
        self.importer.state_set = 0
        self.importer.use_line_count_for_divisions = True
        
        self.importer.import_xml_document(book_doc)
        
        work = self.importer.work
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        self.assertEqual(str(divisions[0]), "Book 1")
        self.assertEqual(str(divisions[1]), "lines 1-32")
    
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
        self.assertEqual(Author.objects.filter(name="Flavius Josephus").count(), 1)
        self.assertEqual(divisions.count(), 1)
        self.assertEqual(verses.count(), 7)
        self.assertEqual(verses[0].indicator, "1")
        self.assertEqual(verses[1].indicator, "2")
        
        # Make sure we slugified the title accordingly
        self.assertEqual(self.importer.work.title_slug, "josephi-vita")
        
        # Make sure the original content
        expected_content = r"""<?xml version="1.0" ?><verse><p>*)emoi\ de\ ge/nos e)sti\n ou)k a)/shmon, a)ll' e)c i(ere/wn a)/nwqen
katabebhko/s. w(/sper d' h( par' e(ka/stois a)/llh ti/s e)stin eu)genei/as
u(po/qesis, ou(/tws par' h(mi=n h( th=s i(erwsu/nhs metousi/a tekmh/rio/n
e)stin ge/nous lampro/thtos. </p></verse>"""
        
        self.assertEqual(verses[0].original_content, expected_content)
    
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
        self.assertEqual(divisions[0].title, "Introduction")
        self.assertEqual(divisions[0].original_title, "intro")
    
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
                self.assertGreater(Verse.objects.filter(division=division).count(), 0)
        
        self.assertEqual(divisions[0].descriptor, "Library")
        
        # 35: 28 sections + 2 text nodes + 3 chapters + 2 div1
        self.assertEqual(divisions.count(), 35)
        self.assertEqual(verses.count(), 28)
        
    def test_load_book_texts_with_head(self):
        
        # This work has multiple text nodes. See if they are imported as separate units
        self.importer.state_set = 0
        book_xml = self.load_test_resource('appian.fw_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        verses = Verse.objects.filter(division__work=self.importer.work)
        
        self.assertEqual(divisions[0].descriptor, "Reg.")
        self.assertEqual(divisions[0].original_title, "*e*k *t*h*s *b*a*s*i*l*i*k*h*s.")
        
        # 2: 1 text nodes, 0 chapters, 1 div1
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(verses.count(), 2)
    
    def test_load_book_editors(self):
        
        # Pre-make the author in order to see if the importer is smart enough to not create a duplicate
        author = Author()
        author.name = "Fenton John Anthony Hort"
        author.save()
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.import_xml_document(book_doc)
        
        self.assertEqual(Author.objects.filter(name="Fenton John Anthony Hort").count(), 1)
        
        self.assertEqual(self.importer.work.editors.all().count(), 2)
        self.assertEqual(self.importer.work.editors.filter(name="Brooke Foss Westcott").count(), 1)
        self.assertEqual(self.importer.work.editors.filter(name="Fenton John Anthony Hort").count(), 1)
    
    def test_load_book_alternate_state_set(self):
        self.importer.state_set = 1  #Using Whiston sections as opposed to the defaults
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 1)
        
    def test_load_book_division_descriptors(self):
        self.importer.state_set = 1
        book_xml = self.load_test_resource('j.bj_gk.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(divisions[0].descriptor, "1")
        
    def test_load_book_line_count_division_titles(self):
        self.importer.state_set = 1
        self.importer.use_line_count_for_divisions = True
        book_xml = self.load_test_resource('aesch.eum_gk.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        #self.assertEqual(divisions.count(), 3)
        #self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 1)
        self.assertEqual(divisions[1].title, "lines 1-33")
        self.assertEqual(divisions[2].title, "lines 34-38")
        
    def test_load_book_empty_sub_divisions(self):
        self.importer.state_set = 0
        
        book_xml = self.load_test_resource('aesch.lib_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions.count(), 6) # Was 3 before cards are always treated as chunks
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 1)
        self.assertEqual(Verse.objects.filter(division=divisions[2]).count(), 0)
    
    def test_load_book_no_chunks(self):
        # See bug #446, http://lukemurphey.net/issues/446
        self.importer.state_set = 0
        
        book_xml = self.load_test_resource('nt_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions[0].original_title, "*k*a*t*a *m*a*q*q*a*i*o*n")
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 4)
        
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
        
        self.assertEqual(divisions[0].original_title, "*Prooi/mion")
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 5)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 5)
        
    def test_load_book_no_verses2(self):
        # See bug #446, http://lukemurphey.net/issues/446
        self.importer.state_set = 0
        self.importer.ignore_division_markers = False
        
        book_xml = self.load_test_resource('plut.068_teubner_gk.xml')
        book_doc = parseString(book_xml)
        
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 0)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 1)
    
    def test_load_book_merged_state_set(self):
        
        self.importer.state_set = None
        book_xml = self.load_test_resource('j.vit_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work)
        
        self.assertEqual(divisions.count(), 2)
        self.assertEqual(Verse.objects.filter(division=divisions[0]).count(), 6)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 1)
    
    def test_load_book_ignore_divs_not_in_refsdecl(self):
        
        self.importer.state_set = 0
        self.importer.ignore_undeclared_divs = True
        file_name = self.get_test_resource_file_name('1_gk.xml')
        self.importer.import_file(file_name)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        # Make sure that the div3 nodes were not treated as chunks
        self.assertEqual(len(divisions), 3) # Would be 5 otherwise
        
    
    def test_load_book_with_sections(self):
        
        self.importer.state_set = 1 #Using Whiston sections as opposed to the defaults
        book_xml = self.load_test_resource('j.aj_gk_portion.xml')
        book_doc = parseString(book_xml)
        work = self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=work).distinct()
        
        self.assertEqual(divisions[1].descriptor, "pr.")
        self.assertEqual(Verse.objects.filter(division__work=work).count(), 5)
        self.assertEqual(Verse.objects.filter(division=divisions[1]).count(), 2)
        
        self.assertEqual(divisions.count(), 5)
        self.assertEqual(divisions[0].type, "Book")
        self.assertEqual(divisions[0].level, 1)
        
        self.assertEqual(divisions[1].type, "Whiston chapter")
        self.assertEqual(divisions[1].level, 2)
        
        self.assertEqual(divisions[0].original_title, r"""*ta/de e)/nestin e)n th=| prw/th| tw=n *)iwsh/pou i(storiw=n
th=s *)ioudai+kh=s a)rxaiologi/as.""")
        self.assertEqual(divisions[2].original_title, r"""*ta/de e)/nestin e)n th=|  b  tw=n *)iwsh/pou i(storiw=n th=s
*)ioudai+kh=s a)rxaiologi/as.""")
        
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
        
        self.assertEqual(Verse.objects.filter(division=divisions[3])[0].original_content, expected_content)
        
    def test_load_book_break_sections(self):
        # See #424, http://lukemurphey.net/issues/424
        
        book_xml = self.load_test_resource('aristd.rhet_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_last_state_is_non_chunk = True
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEqual(divisions.count(), 5)
        self.assertEqual(divisions[1].parent_division.id, divisions[0].id)
        self.assertEqual(divisions[2].parent_division.id, divisions[1].id)
        
        self.assertEqual(divisions[4].parent_division.id, divisions[3].id)
        
    def test_load_book_ignore_divs_and_use_line_numbers(self):
        # See #468, http://lukemurphey.net/issues/468
        
        book_xml = self.load_test_resource('soph.trach_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.use_line_count_for_divisions = True
        self.importer.ignore_division_markers = True
        self.importer.state_set = 0
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEqual(divisions.count(), 4)
        self.assertEqual(divisions[0].title, "lines 1-48")
        
    def test_load_book_only_bottom_division_readable(self):
        # See #502, http://lukemurphey.net/issues/502
        
        book_xml = self.load_test_resource('01_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_leaf_divisions_readable = True
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEqual(divisions.count(), 13)
        self.assertEqual(divisions.filter(readable_unit=True).count(), 11) #is 13 without using only_leaf_divisions_readable = True 
        
    def test_load_book_explicit_division_tags(self):
        # See #503, http://lukemurphey.net/issues/503
        
        book_xml = self.load_test_resource('01_gk.xml')
        book_doc = parseString(book_xml)
        self.importer.only_leaf_divisions_readable = True
        self.importer.division_tags = ["div1", "div2"]
        self.importer.import_xml_document(book_doc)
        
        divisions = Division.objects.filter(work=self.importer.work)
        
        self.assertEqual(divisions.count(), 12) #Should not have made the div3 under chapter 10 a division
        
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
        
        tei_node_portion_doc = parseString(tei_node_portion_xml)
        
        self.assertTrue(PerseusTextImporter.use_line_numbers_for_division_titles(tei_node_portion_doc))
        
        
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
        
        tei_node_portion_doc = parseString(tei_node_portion_xml)
        
        self.assertFalse(PerseusTextImporter.use_line_numbers_for_division_titles(tei_node_portion_doc))
        
    def test_line_count_update(self):
        
        verse_xml = """
        <verse>
            <l>One</l>
            <l>Two</l>
            <l>Three</l>
            <l>Four</l>
        </verse>
        """
        
        verse_doc = parseString(verse_xml)
        
        line_count, _ = PerseusTextImporter.get_line_count(verse_doc)
        
        self.assertEqual(str(line_count), "4")
        
    def test_line_count_update_with_start(self):
        
        verse_xml = """
        <verse>
            <l>Six</l>
            <l>Seven</l>
            <l>Eight</l>
            <l>Nine</l>
        </verse>
        """
        
        verse_doc = parseString(verse_xml)
        
        line_count, _ = PerseusTextImporter.get_line_count(verse_doc, count = 5)
        
        self.assertEqual(str(line_count), "9")
        
    def test_line_count_update_with_specifier(self):
        
        verse_xml = """
        <verse>
            <l>Six</l>
            <l n="7">Seven</l>
            <l>Eight</l>
            <l>Nine</l>
        </verse>
        """
        
        verse_doc = parseString(verse_xml)
        
        line_count, _ = PerseusTextImporter.get_line_count(verse_doc)
        
        self.assertEqual(str(line_count), "9")
