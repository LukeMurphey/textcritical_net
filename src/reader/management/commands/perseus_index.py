from django.core.management.base import BaseCommand

from reader.importer.PerseusBatchImporter import PerseusDataGatherer
from reader.importer.batch_import import ImportPolicy, WorkDescriptor

import os

class Command(BaseCommand):
    help = "Analyzes Perseus XML documents from a directory and produces a CSV containing an index of the works"

    def add_arguments(self, parser):
        parser.add_argument('-d', '--directory',
            dest='directory',
            help='The directory containing the files to import')

        parser.add_argument('-o', '--output',
            dest='output_file',
            default="perseus_stats.csv",
            help='The directory containing the files to import')

        parser.add_argument('-l', '--language',
            dest='language',
            help='The language to restrict results to')

        parser.add_argument('-a', '--author',
            dest='author',
            help='The author to restrict works to')

    def handle(self, *args, **options):
        
        # Get the directory to load the works from
        directory  = options['directory']
        
        if directory is None and len(args) > 0:
            directory = args[0]
        
        # Validate the directory
        if directory is None:
            print "No directory was provided to import"
            return
        
        # Get the output file name, language and author to filter on
        output_file_name  = options['output_file']
        language = options['language']
        author = options['author']
        
        selection_policy = ImportPolicy()
        selection_policy.descriptors.append( WorkDescriptor(author=author, language=language) )
                
        perseus_data_gatherer = PerseusDataGatherer(
                                                      perseus_directory     = directory,
                                                      book_selection_policy = selection_policy.should_be_processed,
                                                      output_file           = output_file_name
                                                   )
        
        print "Exporting stats to", output_file_name
        perseus_data_gatherer.get_stats()
        print "Files from the", os.path.basename(directory), "directory successfully processed"