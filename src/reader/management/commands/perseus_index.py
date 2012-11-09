from django.core.management.base import BaseCommand

from reader.importer.PerseusBatchImporter import ImportPolicy, WorkDescriptor, PerseusDataGatherer

import os
from optparse import make_option

class Command(BaseCommand):

    help = "Analyzes Perseus XML documents from a directory and produces a CSV containing an index of the works"

    option_list = BaseCommand.option_list + (
        make_option("-d", "--directory", dest="directory", help="The directory containing the files to import"),
        make_option("-o", "--output", dest="output_file", default="perseus_stats.csv", help="The path to write the CSV file to"),
        make_option("-l", "--language", dest="language", help="The language to restrict results to"),
        make_option("-a", "--author", dest="author", help="The author to restrict works to"),
    )

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