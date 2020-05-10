import math
import re
from django.shortcuts import get_object_or_404, render
from django.template import loader
from reader.models import Division, WorkAlias, Verse, RelatedWork
from django.http import Http404

def get_chapter_for_division(division):
    """
    Get the division that contains the next part of readable content.
    """
    
    divisions = Division.objects.filter(work=division.work, readable_unit=True, sequence_number__gte=division.sequence_number).order_by("sequence_number")[:1]
    
    if len(divisions) > 0:
        return divisions[0]

def get_chapters_list(division, count=9):
    """
    Get the list of chapters for pagination.
    """
    
    pages_before = math.ceil((count - 1.0) / 2)
    pages_after = math.floor((count - 1.0) / 2)
    
    # Filter down the list to ones within the given work that are readable units
    divisions = Division.objects.filter(work=division.work, readable_unit=True)
    
    # Filter down the list to those in the same parent division
    if division.parent_division is not None:
        divisions = divisions.filter(parent_division=division.parent_division)
        
    # If no parent division was found, then filter the list down to the parent of the first division
    # so that we don't show entries for different divisions in the list
    else:
        
        # Try to get the first division
        first_division = divisions[:1]
        
        # If we got a first division, then filter on this one's parent
        if len(first_division) > 0 and first_division[0].parent_division is not None:
            divisions = divisions.filter(parent_division=first_division[0].parent_division)
        else:
            divisions = divisions.filter(parent_division=None)
    
    # Get the number of pages before
    divisions_before = divisions.filter(sequence_number__lte=division.sequence_number).order_by("-sequence_number")[:pages_before]
    
    divisions_after = divisions.filter(sequence_number__gt=division.sequence_number).order_by("sequence_number")[:pages_after]
    
    final_list = []
    final_list.extend(divisions_before)
    final_list.reverse()
    final_list.extend(divisions_after)
    
    return final_list

def get_division_and_verse(work, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None):
    """
    This function gets the division that is associated with the given descriptor set. If the final division descriptor is 
    actually a verse indicator, then, return the verse indicator.
    
    Arguments:
    work -- The work to get the division from
    division_0 -- The highest division to lookup
    division_1 -- The next highest division to lookup
    division_2 -- The next highest division to lookup
    division_3 -- The next highest division to lookup (this can only be a verse indicator)
    """
    
    # Assume that the descriptors are for divisions
    division = get_division(work, division_0, division_1, division_2, division_3)
    
    if division is not None:
        return division, division_4
    
    # If we couldn't find a division, then let's assume that the last descriptor was for a verse
    if division_3 is not None:
        return get_division(work, division_0, division_1, division_2), division_3
    
    elif division_2 is not None:
        return get_division(work, division_0, division_1), division_2
    
    elif division_1 is not None:
        return get_division(work, division_0), division_1
    
    elif division_0 is not None:
        return get_division(work), division_0

def has_numbered_book_number(division_name):
    
    if division_name is None:
        return None
    
    r = re.compile("([1-9])( .*)")
    if r.match(division_name):
        return True
    else:
        return False
    
def has_lettered_book_number(division_name):
    
    if division_name is None:
        return None
    
    r = re.compile("([IV]+)( .*)")
    if r.match(division_name):
        return True
    else:
        return False

def convert_to_lettered_division_name(division_name):
    
    if division_name is None:
        return None
    
    number_to_letter_map = {
                        '1' : 'I',
                        '2' : 'II',
                        '3' : 'III',
                        '4' : 'IV',
                        '5' : 'V'
                        }
    
    r = re.compile("([1-9])( .*)")
    m = r.match(division_name)
    
    if m and m.groups()[0] in number_to_letter_map:
        converted_character = number_to_letter_map[m.groups()[0]]
        
        return converted_character + m.groups()[1]
    else:
        return division_name

def convert_to_numbered_division_name(division_name):
    
    if division_name is None:
        return None
    
    letter_to_number_map = {
                        'I' : '1',
                        'II' : '2',
                        'III' : '3',
                        'IV' : '4',
                        'V' : '5'
                        }
    
    r = re.compile("([IV]+)( .*)")
    m = r.match(division_name)
    
    if m and m.groups()[0] in letter_to_number_map:
            
        converted_character = letter_to_number_map[m.groups()[0]]
        
        return converted_character + m.groups()[1]
    else:
        return division_name
        
def get_division(work, division_0=None, division_1=None, division_2=None, division_3=None, try_to_match_converting_numbering=True):
    """
    This function gets the division that is associated with the given descriptor set.
    
    Arguments:
    work -- The work to get the division from
    division_0 -- The highest division to lookup
    division_1 -- The next highest division to lookup
    division_2 -- The next highest division to lookup
    division_3 -- The next highest division to lookup
    try_to_match_converting_numbering -- If not none, then attempt get a match by normalizing the division name
    """
    
    # Filter down the list to the division within the given work
    divisions = Division.objects.filter(work=work)
    
    # Get the division if we got four levels deep of descriptors ("1.2.3.4")
    if division_0 is not None and division_1 is not None and division_2 is not None and division_3 is not None:
        
        divisions = divisions.filter(parent_division__parent_division__parent_division__parent_division=None,
                                     parent_division__parent_division__parent_division__descriptor__iexact=division_0,
                                     parent_division__parent_division__descriptor__iexact=division_1,
                                     parent_division__descriptor__iexact=division_2,
                                     descriptor=division_3)
    
    # Get the division if we got three levels deep of descriptors ("1.2.3")
    elif division_0 is not None and division_1 is not None and division_2 is not None:
        
        divisions = divisions.filter(parent_division__parent_division__parent_division=None,
                                     parent_division__parent_division__descriptor__iexact=division_0,
                                     parent_division__descriptor__iexact=division_1,
                                     descriptor=division_2)
        
    # Get the division if we got two levels deep of descriptors ("1.2")
    elif division_0 is not None and division_1:
        
        divisions = divisions.filter(parent_division__parent_division=None,
                                     parent_division__descriptor__iexact=division_0,
                                     descriptor=division_1)
    
    # Get the division if we got one level deep of descriptors ("1")
    elif division_0 is not None:
        divisions = divisions.filter(parent_division=None,
                                     descriptor__iexact=division_0)
    
    # Only grab one
    divisions = divisions[:1]
    
    if len(divisions) > 0:
        return divisions[0]
    else:
        
        if try_to_match_converting_numbering and (has_numbered_book_number(division_0) or has_numbered_book_number(division_1) or has_numbered_book_number(division_2) or has_numbered_book_number(division_3)):
            return get_division(work, convert_to_lettered_division_name(division_0), convert_to_lettered_division_name(division_1), convert_to_lettered_division_name(division_2), convert_to_lettered_division_name(division_3), try_to_match_converting_numbering=False)
        elif try_to_match_converting_numbering and (has_lettered_book_number(division_0) or has_lettered_book_number(division_1) or has_lettered_book_number(division_2) or has_lettered_book_number(division_3)):
            return get_division(work, convert_to_numbered_division_name(division_0), convert_to_numbered_division_name(division_1), convert_to_numbered_division_name(division_2), convert_to_numbered_division_name(division_3), try_to_match_converting_numbering=False)
        
        return None # We couldn't find a matching division, perhaps one doesn't exist with the given set of descriptors?
    
def get_work_page_info(author=None, language=None, title=None, division_0=None, division_1=None, division_2=None, division_3=None, division_4=None, leftovers=None, to_json=False, **kwargs):
    """
    This will get dictionary full of information that can be used to render information about a work.

    This may raise the following exceptions:
    * Http404: the division or work could not be located
    """

    # Some warnings that should be posted to the user
    warnings = []
    
    # Try to get the work
    try:
        work_alias = WorkAlias.objects.get(title_slug=title)
    except WorkAlias.DoesNotExist as e:
        return None

    work = work_alias.work
    
    # Get the chapter
    division, verse_to_highlight = get_division_and_verse(work, division_0, division_1, division_2, division_3, division_4)
    
    # Note a warning if were unable to find the given chapter
    chapter_not_found = False
    
    if leftovers is not None:
        warnings.append(("Section not found", "The place in the text you asked for could not be found (the reference you defined is too deep)."))
        chapter_not_found = True
    
    elif division is None and division_0 is not None:
        warnings.append(("Section not found", "The place in the text you asked for could not be found."))
        chapter_not_found = True
    
    # Start the user off at the beginning of the work
    if division is None:
        division = Division.objects.filter(work=work).order_by("sequence_number")[:1]
        
        if len(division) == 0:
            raise Http404('Division could not be found.')
        else:
            division = division[0]
            
    # Make sure the verse exists
    verse_not_found = False
    
    if chapter_not_found == False and verse_to_highlight is not None:
        if Verse.objects.filter(division=division, indicator=verse_to_highlight).count() == 0:
            warnings.append(("Verse not found", "The verse you specified couldn't be found."))
            verse_not_found = True
    
    # Get the readable unit
    chapter = get_chapter_for_division(division)
    
    # Get the verses to display
    verses = Verse.objects.filter(division=chapter).all()
    
    # Get the divisions that ought to be included in the table of contents
    divisions = Division.objects.filter(work=work, readable_unit=False)
    
    if len(divisions) == 0:
        divisions = None
    
    # Get the list of chapters for pagination
    chapters = get_chapters_list(chapter)
    
    # Get the amount of progress (based on chapters)
    total_chapters     = Division.objects.filter(work=division.work, readable_unit=True).count()
    completed_chapters = Division.objects.filter(work=division.work, readable_unit=True, sequence_number__lte=chapter.sequence_number).count()
    remaining_chapters = total_chapters - completed_chapters
    progress = ((1.0 * completed_chapters) / total_chapters) * 100
    
    # Get the amount of progress (based on chapters within this book)
    total_chapters_in_book = None
    completed_chapters_in_book = None
    remaining_chapters_in_book = None
    progress_in_book = None
    
    if chapter.parent_division is not None:
        total_chapters_in_book = Division.objects.filter(parent_division=chapter.parent_division, readable_unit=True).count()
        completed_chapters_in_book = Division.objects.filter(parent_division=chapter.parent_division, readable_unit=True, sequence_number__lte=chapter.sequence_number).count()
        remaining_chapters_in_book = total_chapters_in_book - completed_chapters_in_book
        progress_in_book = ((1.0 * completed_chapters_in_book) / total_chapters_in_book) * 100
    
    # Get the next and previous chapter number
    previous_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__lt=chapter.sequence_number).order_by('-sequence_number')[:1]
    next_chapter = Division.objects.filter(work=work, readable_unit=True, sequence_number__gt=chapter.sequence_number).order_by('sequence_number')[:1]
    
    if len(previous_chapter) > 0:
        previous_chapter = previous_chapter[0]
    else:
        previous_chapter = None
        
    if len(next_chapter) > 0:
        next_chapter = next_chapter[0]
    else:
        next_chapter = None
    
    # Get related works
    related_works_tmp = RelatedWork.objects.filter(work=work)#.values_list('related_work__title_slug', flat=True)
    related_works = []
    
    # Filter out entries for related works that do not have the related section
    for r in related_works_tmp:
        
        # Make up the list of chapter division descriptors
        args = []
        
        next_division = chapter
    
        while next_division is not None:
            args.insert(0, next_division.descriptor)
            next_division = next_division.parent_division
            
        # Insert the first argument (the related work)
        args.insert(0, r.related_work)
        
        # Try to get the related division
        related_work_division = get_division(*args)
        
        # If we got a match, then the link to the related work should function.
        if related_work_division is not None:
            related_works.append(r.related_work)
    
    # Make the chapter title
    title = work.title
    
    # Add the chapter
    chapter_description = chapter.get_division_description()
    title = title + " " + chapter_description
    
    # Add the verse
    if verse_to_highlight:
        
        if chapter_description.find(".") >= 0:
            title = title + "."
        else:
            title = title + ":"
            
        title = title + verse_to_highlight
    
    data = {
            'title'                      : title,
            'work_alias'                 : work_alias,
            'warnings'                   : warnings,
            'work'                       : work,
            'related_works'              : related_works,
            'verses'                     : verses,
            'divisions'                  : divisions,
            'chapter'                    : chapter,
            'chapters'                   : chapters,
            'authors'                    : work.authors.filter(meta_author=False),
            'next_chapter'               : next_chapter,
            'previous_chapter'           : previous_chapter,
            'verse_to_highlight'         : verse_to_highlight,
            'total_chapters'             : total_chapters,
            'completed_chapters'         : completed_chapters,
            'remaining_chapters'         : remaining_chapters,
            'chapter_not_found'          : chapter_not_found,
            'verse_not_found'            : verse_not_found,
            'progress'                   : progress,
            'progress_in_book'           : progress_in_book,
            'total_chapters_in_book'     : total_chapters_in_book,
            'completed_chapters_in_book' : completed_chapters_in_book,
            'remaining_chapters_in_book' : remaining_chapters_in_book
        }

    if to_json:
        
        # Convert the verses to an HTML blob
        template = loader.get_template('work_verses.html')
        content = template.render(data)

        data = {
                'title'                      : title,
                'work_alias'                 : {
                    'title_slug': work_alias.title_slug
                },
                'work'                       : work_to_json(work),
                'authors'                    : [author_to_json(w) for w in work.authors.filter(meta_author=False)],
                'related_works'              : [work_to_json(w) for w in related_works] ,
                'verse_not_found'            : verse_not_found,
                'warnings'                   : warnings,
                'total_chapters'             : total_chapters,
                'progress_in_book'           : progress_in_book,
                'completed_chapters_in_book' : completed_chapters_in_book,
                'remaining_chapters_in_book' : remaining_chapters_in_book,
                'progress'                   : progress,
                'chapter'                    : division_to_json(chapter),
                'divisions'                  : divisions_to_json(divisions),
                'next_chapter'               : division_to_json(next_chapter),
                'previous_chapter'           : division_to_json(previous_chapter),
                'content'                    : content
        }

    return data

def work_to_json(work):
    if work:
        return {
            'copyright': work.copyright,
            'title': work.title,
            'title_slug': work.title_slug,
            'language': work.language
        }
    else:
        return {
            'copyright': None,
            'title': None,
            'title_slug': None,
            'language': None
        }

def get_division_hierarchy(division):
    ids = []
    current_division = division

    while current_division is not None:
        ids.insert(0, current_division.descriptor) 
        current_division = current_division.parent_division

    return ids

def divisions_to_json(divisions):
    if divisions:
        return [division_to_json(d) for d in divisions]

    return []
def division_to_json(division):
    if division:
        if division.parent_division:
            full_title = division.get_division_description_titles()
            parent_division = division_to_json(division.parent_division)
        else:
            full_title = division.title
            parent_division = None

        # Replace the Greek words in the title
        if full_title:
            full_title = full_title.replace("βοοκ", "book")

        return {
            'sequence_number': division.sequence_number,
            'label': str(division).replace("βοοκ", "book").capitalize(),
            'title': division.title,
            'full_title' : full_title,
            'title_slug': division.title_slug,
            'subtitle': division.subtitle,
            'descriptor': division.descriptor,
            'type': division.type,
            'level': division.level,
            'description': division.get_division_description(),
            'parent_division': parent_division,
            'full_descriptor': "/".join(get_division_hierarchy(division)),
        }

    return None

def author_to_json(author):
    if author:
        return {
            'name': author.name,
            'name_slug': author.name_slug,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'description': author.description
        }
    
    return None