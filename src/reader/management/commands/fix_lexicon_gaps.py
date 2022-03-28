from django.core.management.base import BaseCommand

from reader.models import WordDescription, Lemma, LexiconEntry, WordForm

class Command(BaseCommand):

    help = "Makes foreign keys in the lexicon table point to the missing lemma entries"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Get the LexiconEntry objects that are missing a lemma
        lexicon_entries_gaps = LexiconEntry.objects.filter(lemma__isnull=True)

        # Found
        print("Found", len(lexicon_entries_gaps), "lexicon entries with missing lemmas")
