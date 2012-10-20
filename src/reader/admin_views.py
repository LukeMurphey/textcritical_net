from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.list_detail import object_detail
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
                
            # Convert the state set indicator to a boolean
            try:
                state_set = int(state_set)
            except ValueError:
                pass
                
            # Determine if we are to ignore division markers
            if 'ignore_divisions' in request.POST:
                ignore_divisions = form.cleaned_data['ignore_divisions']
            else:
                ignore_divisions = False
            
            # Determine if we ought to 
            if 'overwrite' in request.POST:
                overwrite = form.cleaned_data['overwrite']
            else:
                overwrite = False
                
            # Get the file contents
            if request.FILES['perseus_file'].multiple_chunks():
                pass
            
            f = request.FILES['perseus_file']
                
            perseus_xml_string = ''
            
            for chunk in f.chunks():
                perseus_xml_string = perseus_xml_string + str(chunk)  
                
            importer = PerseusTextImporter(state_set=state_set, ignore_division_markers=ignore_divisions, overwrite_existing=overwrite)
            work = importer.import_xml_string(perseus_xml_string)
                
            messages.add_message(request, messages.INFO, 'Work successfully imported')
        else:
            
            messages.add_message(request, messages.ERROR, 'Work could not be imported')
            
    else:
        form = ImportPerseusFileForm()
    
    return render_to_response('admin/reader/import_perseus_file.html', {'form' : form,
                                                                        'imported_work' : work}, context_instance=RequestContext(request))