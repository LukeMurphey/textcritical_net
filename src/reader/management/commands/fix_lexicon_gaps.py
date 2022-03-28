from django.core.management.base import BaseCommand

from reader.models import WordDescription, Lemma, LexiconEntry, WordForm
from reader.utils import get_lemma

class Command(BaseCommand):

    help = "Makes foreign keys in the lexicon table point to the missing lemma entries"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Get the LexiconEntry objects that are missing a lemma
        lexicon_entries_gaps = LexiconEntry.objects.filter(lemma__isnull=True)

        # Found
        print("Found", len(lexicon_entries_gaps), "lexicon entries with missing lemmas")

        entries_updated = 0
    
        for lexicon_entry in lexicon_entries_gaps:
            # Find a matching lemma
            lemma = get_lemma(lexicon_entry.form)

            # Assign the lemma
            if lemma is not None:
                lexicon_entry.lemma = lemma
                lexicon_entry.save()

                entries_updated = entries_updated + 1

        print("Updated", entries_updated, "lexicon entries")
