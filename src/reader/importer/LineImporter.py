from reader.language_tools import Greek
from reader.models import Lemma, Case, WordForm, WordDescription, Dialect
import re
import logging
from time import time
from django.db import transaction


class LineImporter():

    @classmethod
    def import_file(cls, file_name, return_created_objects=False, start_line_number=None, logger=None, **kwargs):

        if logger:
            logger.debug("Importing file, file=\"%s\"", file_name)

        # Record the start time so that we can measure performance
        start_time = time()

        # If we are returning the objects, then initialize an array to store them. Otherwise, initialize the count.
        if return_created_objects:
            objects = []
        else:
            objects = 0

        # Initialize a couple more things...
        f = None  # The file handle
        line_number = 0  # The line number

        try:

            # Open the file
            f = open(file_name, 'r')

            # Process each line
            for line in f:

                # Note the line number we are importing
                line_number = line_number + 1

                # If we are importing starting from a particular line number, then skip lines until you get to this point
                if start_line_number is not None and line_number < start_line_number:
                    pass  # Skip this line

                else:
                    # Import the line
                    obj = cls.import_line(line, line_number, **kwargs)

                    if return_created_objects:
                        if obj is not None:
                            objects.append(obj)
                    else:
                        objects = objects + 1
        finally:
            if f is not None:
                f.close()

        if logger:
            logger.info("Import complete, duration=%i", time() - start_time)

        return objects
