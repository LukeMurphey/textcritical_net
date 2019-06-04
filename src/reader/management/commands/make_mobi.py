from django.core.management.base import BaseCommand
from django.db.models import Q
from django.conf import settings

from reader.models import Work
from reader.ebook import MobiConvert

import sys
import os
import traceback
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = "Produces a MOBI from a work"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", action="store_true", default=False, dest="force", help="Force creation of new works even if they already exist")

    def handle(self, *args, **options):
        
        force  = options['force']
        
        # Try to find the work
        try:
            works = Work.objects.all()
            
            for work in works:
                
                epub_file = work.title_slug + ".epub"
                epub_file_full_path = os.path.join( settings.GENERATED_FILES_DIR, epub_file)
                
                # Stop if the ePub file to convert from does not exist
                if not os.path.exists(epub_file_full_path):
                    print "ePub file does not exist, work=%s" % (work.title_slug)
                    return
                
                mobi_file = work.title_slug + ".mobi"
                mobi_file_full_path = os.path.join( settings.GENERATED_FILES_DIR, mobi_file)
                
                # Make the mobi unless it already exist or if we are forcing it
                if force or not os.path.exists(mobi_file_full_path):
                    
                    fname = MobiConvert.convertEpub(work, epub_file_full_path, mobi_file_full_path)
                    
                    if fname is not None:
                        logger.info("Created mobi, filename=%s", fname)
                        print "Created mobi, filename=%s" % (fname)
                    else:
                        logger.warn("Could not create mobi, filename=%s", fname)
                        print "Could not create mobi, filename=%s" % (fname)
            
        except Exception:
            traceback.print_exc()