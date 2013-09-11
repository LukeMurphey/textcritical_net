from epub import EpubBook
from reader.models import Work, Division, Verse, RelatedWork

from django.template import Context, Template
from django.template import loader 

import os
import tempfile
import shutil

class ePubExport(object):
    
    class __Division(object):
        
        def __init__(self, division, toc_node):
            self.toc_node = toc_node
            self.division = division
    
    @classmethod
    def addTitlePage(cls, work, book):
        
        c = Context({"title": work.title,
                     "work" : work
                    })
            
        template = loader.get_template('epub/title.html')
        html = template.render(c).encode("utf-8")
        
        book.addTitlePage(html)
        
    @classmethod
    def addRelatedWorksPage(cls, work, book):
        
        # Gets works listed as related
        related_works_tmp = RelatedWork.objects.filter(work=work)
        related_works = []
        
        for r in related_works_tmp:
            related_works.append(r.related_work)
            
        # Gets works by the same author
        if work.authors.filter(meta_author=False).count() > 0:
            authors_works = Work.objects.filter(authors=work.authors.filter(meta_author=False)[:1])
        else:
            authors_works = None
            
        # If we didn't find any related works, then just move on
        if len(related_works) == 0 and authors_works is None:
            return
            
        c = Context({"title": "Related Works",
                     "work" : work,
                     "related_works" : related_works,
                     "authors_works" : authors_works
                    })
        
        template = loader.get_template('epub/related_works.html')
        html = template.render(c).encode("utf-8")
        
        dest_path = 'related_works.html'
        info_page = book.addHtml('', dest_path, html)
        book.addSpineItem(info_page)
        book.addGuideItem(dest_path, 'Related Works', 'other.related-works-page')
        book.addTocMapNode(dest_path, 'Related Works') 
        
    @classmethod
    def addAboutPage(cls, work, book):
        
        c = Context({"title": "Information",
                     "work" : work
                    })
        
        template = loader.get_template('epub/about.html')
        html = template.render(c).encode("utf-8")
        
        dest_path = 'about.html'
        info_page = book.addHtml('', dest_path, html)
        book.addSpineItem(info_page, True, -100)
        book.addGuideItem(dest_path, 'About', 'other.about-page')
        book.addTocMapNode(dest_path, 'About')
        
    @classmethod
    def addTOCPage(cls, divisions, book):
        
        c = Context({"title": "Table of Contents",
                     "divisions" : divisions
                    })
        
        template = loader.get_template('epub/table_of_contents.html')
        html = template.render(c).encode("utf-8")
        toc_page = book.addHtml('', 'table_of_contents.html', html)
        book.addSpineItem(toc_page, True, -100)
        book.addGuideItem('table_of_contents.html', 'Table of Contents', 'toc-page')
    
    @classmethod
    def addCoverPage(cls, work, book):
        
        c = Context({"title": "Cover",
                     "work" : work
                    })        
        
        template = loader.get_template('epub/cover.html')
        html = template.render(c).encode("utf-8")
        cover_page = book.addHtml('', 'cover.html', html)
        
        book.addGuideItem('cover.html', 'Cover', 'cover')
    
    @classmethod
    def exportWork(cls, work, filename):
        
        book = EpubBook()
        
        book.setTitle(work.title)
        
        for author in work.authors.all():
            book.addCreator(author.name)
        
        cls.addTitlePage(work, book)
        cls.addAboutPage(work, book)
        
        #book.addCover(r'D:\epub\blank.png')
        #local_path = os.path.dirname(os.path.abspath(__file__))
        book.addCss(r'media/stylesheets/epub.css', 'epub.css')
        book.addCss(r'media/stylesheets/bootstrap.css', 'bootstrap.css')
        book.addImage(r'media/images/glyphicons-halflings.png', 'images/glyphicons-halflings.png')
        book.addImage(r'media/images/glyphicons-halflings-white.png', 'images/glyphicons-halflings-white.png')
        book.addImage(r'media/images/epub/Book_Cover.png', 'images/Book_Cover.png')
        
        divisions = Division.objects.filter(work=work).order_by("sequence_number")
        
        cls.divisions_total = divisions.count()
        
        prior_division = None
        division_parents = []
        
        # Export the division
        for division in divisions:
            
            # If this division is deeper than prior division, then add the prior as a parent
            if prior_division is not None and division.level > prior_division.division.level:
                division_parents.append( prior_division )
            
            # If this division is less deep than the prior, then iterate up and pop the parents off
            while len(division_parents) > 0 and division.level < division_parents[-1].division.level:
                division_parents.pop()
            
            # Export the division with the appropriate parent
            if len(division_parents) > 0 and division.level > division_parents[-1].division.level:
                new_division = cls.exportDivision(book, division, division_parents[-1])
            else:
                new_division = cls.exportDivision(book, division)
            
            # Save the prior division
            prior_division = new_division
        
        cls.addRelatedWorksPage(work, book)
        
        # Generate the file
        tmpdir = tempfile.mkdtemp()
        tmpfilename = os.path.join( tmpdir, work.title_slug + ".epub" )
        
        try:
            os.makedirs(os.path.join(tmpdir, 'OEBPS', 'images'))
        except OSError:
            pass
        
        book.createBook(tmpdir)
        EpubBook.createArchive(tmpdir, tmpfilename)
        
        if filename:
            shutil.copyfile(tmpfilename, filename)
            shutil.rmtree(tmpdir)
            return filename
        
        return tmpfilename
        
    @classmethod
    def exportDivision(cls, book, division, parent_division=None):
        
        if division.readable_unit:
        
            c = Context({"chapter": division,
                         "verses" : Verse.objects.filter(division=division).order_by("sequence_number")
                         })
            
            template = loader.get_template('epub/chapter.html')
            html = template.render(c).encode("utf-8")
            
        else:
            c = Context({"division": division
                         })
            
            template = loader.get_template('epub/section.html')
            html = template.render(c).encode("utf-8")
            
        epub_division = book.addHtml('', str(division.sequence_number) + '.html', html)
        book.addSpineItem(epub_division)
        
        if parent_division is not None:
            print "Parent of ", str(division), " is ", str(parent_division.division)
            toc_node = book.addTocMapNode(epub_division.destPath, division.descriptor, division.level) #, parent = parent_division.toc_node)
        else:
            toc_node = book.addTocMapNode(epub_division.destPath, division.descriptor)
        
        #print "Successfully exported division:", division.descriptor
        return cls.__Division(division, toc_node)