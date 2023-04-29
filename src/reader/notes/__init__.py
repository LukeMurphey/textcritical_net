from django.db.models import Q
from reader.models import Work, Note, RelatedWork
from reader.utils.work_helpers import get_division_and_verse, get_division

def get_related_notes(user, work_slug, division_descriptor, search=None, page=None, count=10, include_notes_for_related_works = True):
  
  # Get the notes for the logged in user
  notes = Note.objects.filter(user=user)
  related_works = None
  
  if (work_slug):
      work = Work.objects.get(title_slug=work_slug)
      
      works_filter = Q(notereference__work_title_slug=work_slug)
      
      if include_notes_for_related_works:
          related_works = RelatedWork.objects.filter(work=work)

          for related_work in related_works:
              works_filter = works_filter | Q(notereference__work_title_slug=related_work.related_work.title_slug)
          
      notes = notes.filter(works_filter)
      
  if (division_descriptor and work):
      # Get the division requested
      division, verse_indicator = get_division_and_verse(work, *division_descriptor.split("/"))
      
      division_filter = Q(notereference__division_full_descriptor=division.get_full_division_indicator_string()) | Q(notereference__division_id=division.id)
      
      # Get the divisions for the related works
      if related_works:
          
          for related_work in related_works:
              related_division = get_division(related_work.related_work, *division.get_division_indicators())
              
              # Related division found, add the filter
              if related_division:
                  division_filter = division_filter | Q(notereference__division_full_descriptor=related_division.get_full_division_indicator_string()) | Q(notereference__division_id=related_division.id)

      # Find notes for the division
      notes = notes.filter(division_filter)
      
      # Filter down to the verse if necessary
      if (verse_indicator):
          notes = notes.filter(notereference__verse_indicator=verse_indicator)
      
  if (search):
      notes = notes.filter((Q(title__icontains=search) | Q(text__icontains=search)))

  # Paginate the data
  if (page):
      start = page * count
      end = start + count
      
      # Cut the results down to the page
      notes = notes[start:end]
      
  return notes
