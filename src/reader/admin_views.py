from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from datetime import datetime

from reader.forms import ImportPerseusFileForm
from reader.importer.Perseus import PerseusTextImporter

@staff_member_required
def import_perseus_file(request):
    
    work = None
    start_time = datetime.now()
    
    # If this is POST, then check the contents against the form
    if request.method == 'POST':
        
        form = ImportPerseusFileForm(request.POST, request.FILES)
        
        # Make sure that the form is valid
        if form.is_valid():
            """
            overwrite = False
            
            if 'overwrite' in request.POST and form.cleaned_data['overwrite'] != '':
                overwrite = True
            """
                
            if 'state_set' in request.POST and len(form.cleaned_data['state_set']) > 0:
                state_set = form.cleaned_data['state_set']
            else:
                state_set = 0
                
            # Convert the state set indicator to an integer
            try:
                state_set = int(state_set)
            except ValueError:
                pass
                
            # Determine if we are to ignore division markers
            if 'ignore_divisions' in request.POST:
                ignore_divisions = form.cleaned_data['ignore_divisions']
            else:
                ignore_divisions = False
            
            # Determine if we ought to overwrite existing works
            if 'overwrite' in request.POST:
                overwrite = form.cleaned_data['overwrite']
            else:
                overwrite = False
            
            # Determine if we ought to throw out content that exists before a milestone was observed
            if 'ignore_content_before_milestones' in request.POST:
                ignore_content_before_milestones = form.cleaned_data['ignore_content_before_milestones']
            else:
                ignore_content_before_milestones = False
                
            # Determine if we ought to throw out divisions that are not in the refsdecl
            if 'ignore_undeclared_divs' in request.POST:
                ignore_undeclared_divs = form.cleaned_data['ignore_undeclared_divs']
            else:
                ignore_undeclared_divs = False
                
            # Determine if we are to ignore division markers
            if 'ignore_notes' in request.POST:
                ignore_notes = form.cleaned_data['ignore_notes']
            else:
                ignore_notes = False

            # Handle the division minimum
            if 'division_min' in request.POST and len(form.cleaned_data['division_min']) > 0:
                division_min = form.cleaned_data['division_min']
            else:
                division_min = None
                
            # Convert the division minimum to a integer
            try:
                if division_min is not None:
                    division_min = int(division_min)
            except ValueError:
                pass
            
            # Get the file contents
            if request.FILES['perseus_file'].multiple_chunks():
                pass
            
            f = request.FILES['perseus_file']
                
            perseus_xml_string = ''
            
            for chunk in f.chunks():
                perseus_xml_string = perseus_xml_string + str(chunk)  
                
            importer = PerseusTextImporter(state_set=state_set,
                                           ignore_division_markers=ignore_divisions,
                                           overwrite_existing=overwrite,
                                           ignore_content_before_first_milestone=ignore_content_before_milestones,
                                           ignore_undeclared_divs=ignore_undeclared_divs,
                                           division_min=division_min,
                                           ignore_notes=ignore_notes)

            work = importer.import_xml_string(perseus_xml_string)
                
            messages.add_message(request, messages.INFO, 'Work successfully imported')
        else:
            
            messages.add_message(request, messages.ERROR, 'Work could not be imported')
            
    else:
        form = ImportPerseusFileForm()
    
    return render_to_response('admin/reader/import_perseus_file.html', {'form' : form,
                                                                        'imported_work' : work}, context_instance=RequestContext(request))