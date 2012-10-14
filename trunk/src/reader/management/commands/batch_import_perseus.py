from django.core.management.base import BaseCommand

from reader.importer.PerseusBatchImporter import JSONImportPolicy, PerseusBatchImporter

import os
from optparse import make_option

class Command(BaseCommand):

    help = "Imports all Perseus XML documents from a directory that match the import policy"

    option_list = BaseCommand.option_list + (
        make_option("-d", "--directory", dest="directory", help="The directory containing the files to import"),
        make_option("-o", "--overwrite", action="store_false", dest="overwrite", default=False, help="Overwrite and replace existing items"),
    )

    def handle(self, *args, **options):
        
        directory  = options['directory']
        
        if directory is None and len(args) > 0:
            directory = args[0]
        
        # Validate the arguments
        if directory is None:
            print "No directory was provided to import"
            return
        
        overwrite = options['overwrite']
        
        if overwrite is None:
            overwrite = False
        else:
            overwrite = True
        
        print "Importing files from", os.path.basename(directory)
        
        selection_policy = JSONImportPolicy()
        selection_policy.load_policy("reader/importer/perseus_import_policy.json")
                
        perseus_batch_importer = PerseusBatchImporter(
                                                      perseus_directory     = directory,
                                                      book_selection_policy = selection_policy.should_be_imported,
                                                      overwrite_existing    = overwrite )
        
        perseus_batch_importer.do_import()
        
        print "Files from the", os.path.basename(directory), "directory successfully imported"