from django.core.management.base import BaseCommand
from django.db.models import Q
from django.conf import settings

from reader.models import Work
from reader.ebook import ePubExport

import sys
import os
from optparse import make_option
import traceback
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = "Produces an ePub from a work"

    option_list = BaseCommand.option_list + (
        make_option("-f", "--force", action="store_true", default=False, dest="force", help="Force creation of new works even if they already exist"),
    )

    def handle(self, *args, **options):
        
        force  = options['force']
        
        # Try to find the work
        try:
            works = Work.objects.all()
            
            for work in works:
                
                epub_file = work.title_slug + ".epub"
                epub_file_full_path = os.path.join( settings.GENERATED_FILES_DIR, epub_file)
                
                # Make the epub unless it already exist or if we are forcing it
                if force or not os.path.exists(epub_file_full_path):
                    fname = ePubExport.exportWork(work, epub_file_full_path)
                    logger.info("Created epub, filename=%s", fname)
                    print "Created epub, filename=", fname
            
        except Exception as e:
            traceback.print_exc()