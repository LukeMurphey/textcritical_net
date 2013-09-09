from django.core.management.base import BaseCommand
from django.db.models import Q

from reader.models import Work
from reader.ebook import ePubExport

import sys
import os
from optparse import make_option
import traceback

class Command(BaseCommand):

    help = "Produces an ePub from a work"

    option_list = BaseCommand.option_list + (
        make_option("-w", "--work", dest="work", help="The work to produce an eBook for"),
        make_option("-f", "--file", dest="filename", help="The location to place the exported file"),
    )

    def handle(self, *args, **options):
        
        work_title  = options['work']
        
        if work_title is None and len(args) > 0:
            work_title = args[0]
            
        if work_title is None:
            print "No work title provided"
            return
        
        filename  = options['filename']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            filename = work_title
            return
        
        # Try to find the work
        try:
            work = Work.objects.get( Q(title=work_title) | Q(title_slug=work_title) )
            
            ePubExport.exportWork(work, filename)

        except Work.DoesNotExist:
            print "Work could not be found with the given title"
        except Exception as e:
            traceback.print_exc()