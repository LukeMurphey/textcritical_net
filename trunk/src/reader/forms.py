from django import forms

class ImportPerseusFileForm(forms.Form):
    perseus_file = forms.FileField()
    state_set = forms.CharField( required=False, help_text='Enter an integer defining which state set to use (by default, the first will be used)')
    overwrite = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Replaces an existing book with the contents of this book.')
    ignore_divisions = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores division markers in the book.')
    ignore_content_before_milestones = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores content until a milestone is observed.')
    ignore_undeclared_divs = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Ignores divisions that are undeclared.')