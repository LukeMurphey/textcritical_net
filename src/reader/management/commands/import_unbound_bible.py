from django.core.management.base import BaseCommand

from reader.importer.unbound_bible import UnboundBibleTextImporter
from reader.importer.batch_import import JSONImportPolicy

import sys
import os

class Command(BaseCommand):

    help = "Imports Unbound Bible documents"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="filename", help="The file to import")

    def handle(self, *args, **options):
        
        filename  = options['filename']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            print "No filename was provided to import"
            return
        
        # Get the path to the import policy accounting for the fact that the command may be run outside of the path where manage.py resides
        import_policy_file = os.path.join( os.path.split(sys.argv[0])[0], "reader", "importer", "unbound_bible_import_policy.json")
        
        import_policy = JSONImportPolicy()
        import_policy.load_policy( import_policy_file )
        
        print "Importing", os.path.basename(filename)
        importer = UnboundBibleTextImporter(import_policy=import_policy.should_be_processed)
        importer.import_file(filename)
        
        print os.path.basename(filename), "successfully imported"