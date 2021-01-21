from django import forms

class URLForm(forms.Form):
    url = forms.CharField(label='Enter Movie Name', max_length=500)