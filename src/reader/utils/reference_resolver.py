import re
from reader.models import Division
from django.template.defaultfilters import slugify
from django.urls import reverse
from reader.utils.work_helpers import get_division_and_verse

def assign_divisions(ref_components):

    division_0, division_1, division_2, division_3, division_4 = None, None, None, None, None

    if len(ref_components) >= 5:
        division_0, division_1, division_2, division_3, division_4 = ref_components[:5]
    elif len(ref_components) == 4:
        division_0, division_1, division_2, division_3 = ref_components
    elif len(ref_components) == 3:
        division_0, division_1, division_2 = ref_components
    elif len(ref_components) == 2:
        division_0, division_1 = ref_components
    elif len(ref_components) == 1:
        division_0 = ref_components[0]

    return division_0, division_1, division_2, division_3, division_4

def swap_slugs(divisions_with_spaces, *args):

    results = []

    for arg in args:
        if arg is not None:
            for d in divisions_with_spaces:
                arg = arg.replace(slugify(d['descriptor']), d['descriptor'])

        results.append(arg)

    return results

def parse_reference_and_get_division_and_verse(regex, escaped_ref, work, divisions_with_spaces):

    # Try parsing the reference normally
    division_0, division_1, division_2, division_3, division_4 = assign_divisions(
        re.split(regex, escaped_ref))

    # Swap back the slugs
    division_0, division_1, division_2, division_3, division_4 = swap_slugs(
        divisions_with_spaces, division_0, division_1, division_2, division_3, division_4)

    # Try to resolve the division
    division, verse_to_highlight = get_division_and_verse(
        work, division_0, division_1, division_2, division_3, division_4)

    return division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4

def resolve_division_reference(work, ref):
    '''
    Takes a string and resolves the reference to the division and verse reference.
    
    This returns a tuple with the following:
    
      division: an instance of Division that this refers to
      divisions: the set of division descriptors for the division and its parents
      verse: the verse descriptor of the verse if the reference points to one
      url_path: that path to refer to this passage 
    '''
    # Get the division names that have spaces in them
    divisions_with_spaces = Division.objects.filter(
        work=work, descriptor__contains=' ').values('descriptor')

    # Start making the arguments the we need for making the URL
    args = [work.title_slug]

    # Swap out the titles of the divisions with spaces in the name with the title slug (we will swap them back when we are done)
    escaped_ref = ref + ''

    for d in divisions_with_spaces:
        escaped_ref = escaped_ref.replace(
            d['descriptor'], slugify(d['descriptor']))

    # Try to resolve the division
    division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse(
        '[ .:]+', escaped_ref, work, divisions_with_spaces)

    # If parsing it normally didn't parse right, then try without using the period as a separator
    if division is None and division_0 is not None:
        division, verse_to_highlight, division_0, division_1, division_2, division_3, division_4 = parse_reference_and_get_division_and_verse(
            '[ :]+', escaped_ref, work, divisions_with_spaces)

    l = [division_0, division_1, division_2, division_3, division_4]

    args.extend([x for x in l if x is not None])

    # Get the full reference of the divisions
    divisions = [x for x in l if x is not None]

    # Drop the last division ID since this is the verse if one was found
    if verse_to_highlight:
        divisions = divisions[:-1]
        
    return division, divisions, verse_to_highlight, reverse('read_work', args=args)
