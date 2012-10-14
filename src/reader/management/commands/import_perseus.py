from django.core.management.base import BaseCommand

from reader.importer.Perseus import PerseusTextImporter

import os
from optparse import make_option

class Command(BaseCommand):

    help = "Imports Perseus XML documents"

    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="filename", help="The file to import"),
        make_option("-s", "--state_set", dest="state_set", help="The state set to use", default=0)
    )

    def handle(self, *args, **options):
        
        filename  = options['filename']
        state_set = options['state_set']
        
        if filename is None and len(args) > 0:
            filename = args[0]
        
        # Validate the arguments
        if filename is None:
            print "No filename was provided to import"
            return
        
        try:
            if state_set not in [None, "*"]:
                state_set = int(state_set)
        except ValueError:
            print "The state_set is invalid"
            return
        
        print "Importing ", os.path.basename(filename)
        importer = PerseusTextImporter(state_set=state_set)
        importer.import_file(filename)
        
        print os.path.basename(filename), "successfully imported"