from django.core.management.base import BaseCommand

from reader.importer.PerseusBatchImporter import PerseusBatchImporter
from reader.importer.batch_import import JSONImportPolicy
import datetime

import os
import sys

class Command(BaseCommand):
    help = "Imports all Perseus XML documents from a directory that match the import policy"

    def add_arguments(self, parser):
        parser.add_argument('-d', '--directory',
            dest='directory',
            help='The directory containing the files to import')

        parser.add_argument('-o', '--overwrite',
            action="store_true",
            dest="overwrite",
            default=False,
            help="Overwrite and replace existing items")

        parser.add_argument("-t", "--test",
            action="store_true",
            dest="test",
            help="Output the import parameters for any works that would be imported")

    def handle(self, *args, **options):
        
        directory  = options['directory']
        
        if directory is None and len(args) > 0:
            directory = args[0]
        
        # Validate the arguments
        if directory is None:
            print("No directory was provided to import")
            return
        
        overwrite = options['overwrite']
        
        if overwrite is None:
            overwrite = False
        elif overwrite in [True, False]:
            pass # Already a boolean
        elif overwrite.lower() in ["true", "1"]:
            overwrite = True
        else:
            overwrite = False

        test = options['test']

        if test is None:
            test = False
        elif test in [True, False]:
            pass # Already a boolean
        elif test.lower() in ["true", "1"]:
            test = True
        else:
            test = False

        # Get the path to the import policy accounting for the fact that the command may be run outside of the path where manage.py resides
        import_policy_file = os.path.join( os.path.split(sys.argv[0])[0], "reader", "importer", "perseus_import_policy.json")
        
        selection_policy = JSONImportPolicy()
        selection_policy.load_policy(import_policy_file)
        
        perseus_batch_importer = PerseusBatchImporter(
                                                      perseus_directory= directory,
                                                      book_selection_policy = selection_policy.should_be_processed,
                                                      overwrite_existing = overwrite,
                                                      test = test)
        
        if test:
            print("Testing import for files from", directory)
        else:
            print("Importing files from", directory)

        perseus_batch_importer.do_import()

        if test:
            print("Files from the", directory, "evaluated")
        else:
            print("Files from the", directory, "directory successfully imported")
            print(datetime.datetime.now())
