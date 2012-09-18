from django import forms

class ImportPerseusFileForm(forms.Form):
    perseus_file = forms.FileField()
    #overwrite = forms.BooleanField( required=False, widget=forms.CheckboxInput(attrs={'class':'Checkbox'}), help_text='Replaces an existing book with the contents of this book.')
    state_set = forms.CharField( required=False, help_text='Enter an integer defining which state set to use (by default, the first will be used)')
    