from django.core.management.base import BaseCommand
from reader.models import Work, RelatedWork
from django.db.models import Q

import os
import sys
from optparse import make_option

class Command(BaseCommand):

    help = "Imports all Perseus XML documents from a directory that match the import policy"

    option_list = BaseCommand.option_list + (
        make_option("-w", "--work", dest="work", help="The work to look for possible relationships"),
        make_option("-t", "--test", action="store_true", dest="test", help="Just output "),
    )

    def handle(self, *args, **options):

        # Get the work 
        work_title  = options['work']
        
        if work_title is None and len(args) > 0:
            work_title = args[0]

        # Determine if this is just a test
        test = options['test']

        if test is None:
            test = False
        elif test in [True, False]:
            pass # Already a boolean
        elif test.lower() in ["true", "1"]:
            test = True
        else:
            test = False

        # Try to find the work
        try:
            work = Work.objects.get(Q(title=work_title) | Q(title_slug=work_title))

            print "Looking for works that are related..."
            related_works = RelatedWork.find_related_for_work(work, test=test)
            print "Done"

            if test:
                print "Related works found:"
                number = 1
                for work in related_works:
                    print "   ", str(number) + ")", str(work), "(" + work.title_slug + ")" 
        except Work.DoesNotExist:
            print "Work could not be found with the given title"
