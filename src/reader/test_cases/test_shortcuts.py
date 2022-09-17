from . import TestReader
from reader.shortcuts import convert_xml_to_html5, convert_xml_to_text
from reader.templatetags.reader_extras import perseus_xml_to_html5

class TestShortcuts(TestReader):
    
    def time_conversion(self):
        import time
        
        start = time.time()
        
        for i in range(0, 10000):
            self.test_process_text()
        
        print("Completed", time.time() - start)
    
    def test_process_text(self):
        
        original_content = r"""<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>
</verse>"""

        expected_result = r"""<verse>
    <span class="head">*(ikanw=s <span class="num" data-ref="some_ref">d</span> me\n </span>
</verse>"""

        actual_result = convert_xml_to_html5(original_content, new_root_node_tag_name="verse", return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_text_entity(self):
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>&amp;
</verse>"""

        expected_result = r"""<verse>
    <span class="head">*(ikanw=s <span class="num" data-ref="some_ref">d</span> me\n </span>&amp;
</verse>"""

        actual_result = convert_xml_to_html5(original_content, new_root_node_tag_name="verse", return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_custom_transformation(self):
        
        def node_transformation_fx(tag, attrs, parent, document):
            
            if tag == "num":
                
                new_node = document.createElement("strong")
                
                i = 0
                for name, value in attrs:
                    
                    i = i + 1
                    new_node.setAttribute("attr" + str(i), name + "_" + value)
                    
                return new_node
        
        original_content = r"""
<verse>
    <head>foo <num ref="some_ref">d</num> bar</head>
</verse>"""

        expected_result = r"""<verse>
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
        expected_result = r"""<span class="verse">
    <span class="head">Ἱκανῶς <span class="num" data-ref="some_ref">δ</span> μὲν </span>
</span>"""

        actual_result = convert_xml_to_html5(original_content, language=language, return_as_str=True)
        
        self.assertEqual(expected_result, actual_result)
        
    def test_process_text_multi_language_transforms(self):
        
        original_content = r"""<verse>koti/nois<note anchored="yes" place="unspecified" resp="ed">
                  <foreign lang="greek">koti/nois</foreign> MSS.; <foreign lang="greek">kolwnoi=s</foreign>(hills' Bekker, adopting the correction of Coraës.</note>  kai\ pa/gois</verse>"""

        language = "Greek"

        actual_result = perseus_xml_to_html5(original_content, language=language)

        self.assertIn('<span class="word">κοτίνοις</span>', actual_result)
        
    def test_convert_xml_to_text(self):
        
        
        original_content = r"""
<verse>
    <head>*(ikanw=s <num ref="some_ref">d</num> me\n </head>
</verse>"""

        language = "Greek"
        expected_result = r"""Ἱκανῶς δ μὲν"""

        actual_result = convert_xml_to_text(original_content, language=language)
        
        self.assertEqual(expected_result, actual_result)
