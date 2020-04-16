from . import TestReader
from reader.models import WikiArticle

class TestWikiArticle(TestReader):
    
    def test_get_wiki_article(self):
        wiki = WikiArticle(search="M. Antonius Imperator Ad Se Ipsum", article="Meditations")
        wiki.save()
        
        wiki2 = WikiArticle(search="M. Antonius Imperator Ad Se Ipsum Marcus Aurelius", article="Meditations")
        wiki2.save()
        
        # Try a lookup with the string
        article = WikiArticle.get_wiki_article("M. Antonius Imperator Ad Se Ipsum")
        self.assertEqual(article, "Meditations")
        
        # Try a lookup with an array of strings
        article = WikiArticle.get_wiki_article(["M. Antonius Imperator Ad Se Ipsum"])
        self.assertEqual(article, "Meditations")
        
        # Try a lookup with an array of strings where the first one doesn't match
        article = WikiArticle.get_wiki_article(["Tree", "M. Antonius Imperator Ad Se Ipsum"])
        self.assertEqual(article, "Meditations")
        
        # Try a lookup that fails
        article = WikiArticle.get_wiki_article(["Tree", "Frogs"])
        self.assertEqual(article, None)
