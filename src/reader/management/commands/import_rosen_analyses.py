from django.core.management.base import BaseCommand

from reader.importer.Rosen import RosenAnalysesImporter

import os

class Command(BaseCommand):

    help = "Imports Rosen (Babylon) analyses"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="filename", help="The file to import")
        parser.add_argument("-l", "--line_number", dest="line_number", help="The line-number to begin")

    def handle(self, *args, **options):
        
        filename  = options['filename']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            print("No filename was provided to import")
            return
        
        # Get the line number
        line_number = options['line_number']
        
        if line_number is not None:
            line_number = int(line_number)
        
        print("Importing ", filename)
        importer = RosenAnalysesImporter()
        importer.import_file(filename, start_line_number=line_number)
        
        print(os.path.basename(filename), "successfully imported")