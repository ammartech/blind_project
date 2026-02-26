from django import forms

from service.models import GlossaryTerm


class TermForm(forms.ModelForm):
    """Glossary term form - uses the consolidated GlossaryTerm model."""

    class Meta:
        model = GlossaryTerm
        fields = ('term', 'definition', 'pronunciation_hint', 'category')
        widgets = {
            'term': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'المصطلح',
            }),
            'definition': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'التعريف',
            }),
            'pronunciation_hint': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'تلميح النطق (اختياري)',
            }),
            'category': forms.Select(attrs={
                'class': 'input select',
            }),
        }
