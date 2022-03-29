from time import time
import re

class GreekAnalysesParser():
    COMMENT_RE = re.compile("[#].*")
    FORMS_RE = re.compile("[^|]+")
    MAIN_ANALYSIS_RE = re.compile("(.*):(.*):(.*)")
    PARSE_FIND_ATTRS = re.compile("[a-zA-Z0-9_]+")

    def clean_up_form(self, form):
        """
        Clean up the form.
        """
        if form.startswith("!"):
            return form[1:].strip()

        return form.strip()

    def process_word_description(self, form, lemma_form, meaning, details, attrs, definition):
        return None

    def import_line(self, form, entry, line_number=None, raise_exception_on_match_failure=False):
        """
        Parse an entry in the analysis file.

        Example:
            !άβαις|!άβαις
            ἥβη : youthful prime : fem dat pl (doric)

        Arguments:
        entry -- A line in the greek-analysis file
        line_number -- The line number associated with the entry
        """

        # Keep a list of the parse forms
        parsed_forms = []

        # Break up the forms into a list
        possibleForms = GreekAnalysesParser.FORMS_RE.findall(form)

        # Clean up the forms
        for i in range(len(possibleForms)):
            possibleForms[i] = self.clean_up_form(possibleForms[i])

        # Break up the entry if it has multiple forms
        definitions = entry.split("<br>")

        # Handle each definition
        for possibleForm in possibleForms:
            for definition in definitions:
                parsed_entry = GreekAnalysesParser.MAIN_ANALYSIS_RE.match(definition)
                
                lemma_form = parsed_entry.group(1).strip()
                meaning = parsed_entry.group(2).strip()
                details = parsed_entry.group(3).strip()

                # Parse into a list of attributes
                attrs = GreekAnalysesParser.PARSE_FIND_ATTRS.findall(details)
    
                word_description = self.process_word_description(possibleForm, lemma_form, meaning, details, attrs, definition)

                if word_description is not None:
                    parsed_forms.append(word_description)

        # Return what we parsed
        return parsed_forms

    def parse_file(self, file_handle, return_created_objects=False, start_line_number=None, logger=None, raise_exception_on_match_failure=False, **kwargs):

        # Record the start time so that we can measure performance
        start_time = time()

        # If we are returning the objects, then initialize an array to store them. Otherwise, initialize the count.
        if return_created_objects:
            objects = []
        else:
            objects = 0

        # Initialize a couple more things...
        line_number = 0  # The line number

        # This will be the line
        formLine = None

        # Process each line
        for line in file_handle:

            # Note the line number we are importing
            line_number = line_number + 1

            # If we are importing starting from a particular line number, then skip lines until you get to this point
            if start_line_number is not None and line_number < start_line_number:
                pass # Skip this line

            else:
                # Stop if this is a comment
                if GreekAnalysesParser.COMMENT_RE.match(line):
                    if formLine is not None:
                        if raise_exception_on_match_failure:
                            raise Exception("Line %i: Observed a comment line, but we have a form line" % line_number)
                        
                        if logger:
                            logger.warn("Line %i: Observed a comment line, but we have a form line", line_number)

                        formLine = None
                
                # Stop if this is an empty line
                elif line.strip() == "":
                    if formLine is not None:
                        if raise_exception_on_match_failure:
                            raise Exception("Line %i: Observed an empty line, but we have a form line" % line_number)
                        
                        if logger:
                            logger.warn("Line %i: Observed an empty line, but we have a form line", line_number)

                        formLine = None

                # These are supposed to be two rows; add the first row as the one with the list of matching forms
                elif formLine is None:
                    formLine = line

                elif formLine is not None:

                    # Import the line
                    obj = self.import_line(formLine, line, line_number, **kwargs)

                    # Reset the form line since we are done with it
                    formLine = None

                    # Create the entries
                    if return_created_objects:
                        if obj is not None:
                            objects.extend(obj)
                    else:
                        objects = objects + len(obj)

        if logger:
            logger.info("Parsing complete, duration=%i", time() - start_time)

        return objects
