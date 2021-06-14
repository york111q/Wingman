from django import forms
from django.core.validators import FileExtensionValidator

class HtmlFileForm(forms.Form):
    file = forms.FileField(required=False,
                           label="Html file:",
                           validators=[FileExtensionValidator(allowed_extensions=['html'])]
                           )
