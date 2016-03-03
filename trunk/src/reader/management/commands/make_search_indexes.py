from django.core.management.base import BaseCommand

from reader.contentsearch import WorkIndexer
from reader.models import Work
from django.db.models import Q

from optparse import make_option

class Command(BaseCommand):

    help = "Creates the indexes necessary for facilitating searches"

    option_list = BaseCommand.option_list + (
        make_option("-w", "--work", dest="work", help="The work to index"),
        make_option("-c", "--clear", action="store_true", dest="clear_indexes", default=False, help="Clear the existing indexes before starting"),
        make_option("-f", "--fresh", action="store_true", dest="fresh_index", default=False, help="Start with a fresh index for the given work before re-indexing it")
    )

    def handle(self, *args, **options):
        
        work_title  = options['work']
        
        if work_title is None and len(args) > 0:
            work_title = args[0]
            
        
        clear_indexes  = options['clear_indexes']
        
        # Make the directory if it does not exist
        if clear_indexes or not WorkIndexer.index_dir_exists():
            WorkIndexer.get_index(create=True)
        
        # Index all works if no work was provided
        if work_title is None:
            print "Creating search indexes..."
            WorkIndexer.index_all_works()
            print "Search indexes successfully created"
            
        # Index the provided work
        else:
            
            # Try to find the work
            try:
                work = Work.objects.get( Q(title=work_title) | Q(title_slug=work_title) )
               
                fresh_index  = options['fresh_index']
                
                if fresh_index:
                    print "Deleting existing index for work..."
                    WorkIndexer.delete_work_index(work)
                    print "Existing index for work successfully deleted"
                
                print "Creating search indexes for work..."
                WorkIndexer.index_work(work)
                print "Search indexes successfully created"
            except Work.DoesNotExist:
                print "Work could not be found with the given title"