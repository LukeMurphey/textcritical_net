from django.core.management.base import BaseCommand

from reader.importer.Diogenes import DiogenesAnalysesImporter

import os
from optparse import make_option

class Command(BaseCommand):

    help = "Imports Diogenes analyses"

    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="filename", help="The file to import"),
        make_option("-l", "--line_number", dest="line_number", help="The line-number to begin")
    )

    def handle(self, *args, **options):
        
        filename  = options['filename']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            print "No filename was provided to import"
            return
        
        # Get the line number
        line_number = options['line_number']
        
        if line_number is not None:
            line_number = int(line_number)
        
        print "Importing ", filename
        importer = DiogenesAnalysesImporter()
        importer.import_file(filename, start_line_number=line_number)
        
        print os.path.basename(filename), "successfully imported"