from django import forms

class URLForm(forms.Form):
    URL = forms.CharField(label='URL', max_length=500)