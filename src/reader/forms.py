from django import forms

class ImportPerseusFileForm(forms.Form):
    perseus_file = forms.FileField()
    state_set = forms.CharField( required=False, help_text='Enter an integer defining which state set to use (by default, the first will be used)')
    overwrite = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Replaces an existing book with the contents of this book.')
    ignore_divisions = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores division markers in the book.')
    ignore_content_before_milestones = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores content until a milestone is observed.')
    ignore_undeclared_divs = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores divisions that are undeclared.')
    division_min = forms.CharField( required=False, help_text='Enter an integer defining how deep to ignore divisions (use to ignore some deeply nested notes, like "div2")')
    ignore_notes = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores embedded notes.')

class ImportPerseusFileFormByPolicy(forms.Form):
    perseus_file = forms.FileField()
