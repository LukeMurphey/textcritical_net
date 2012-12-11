from django.core.management.base import BaseCommand

from reader.importer.Diogenes import DiogenesLemmataImporter

import os
from optparse import make_option

class Command(BaseCommand):

    help = "Imports Diogenes lemmata"

    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="filename", help="The file to import"),
    )

    def handle(self, *args, **options):
        
        filename  = options['filename']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            print "No filename was provided to import"
            return
        
        print "Importing ", filename
        importer = DiogenesLemmataImporter()
        importer.import_file(filename)
        
        print os.path.basename(filename), "successfully imported"