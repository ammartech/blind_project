from django import forms

from .models import GlossaryTerm, Inquiry


class InquiryCreateForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('title', 'question_text', 'question_audio', 'priority')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'عنوان الاستفسار',
            }),
            'question_text': forms.Textarea(attrs={
                'class': 'input',
                'rows': 5,
                'placeholder': 'اكتب سؤالك هنا...',
            }),
            'question_audio': forms.FileInput(attrs={
                'class': 'input-file',
                'accept': 'audio/*',
            }),
            'priority': forms.Select(attrs={
                'class': 'input select',
            }),
        }


class TranscribeForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('transcription_text',)
        widgets = {
            'transcription_text': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'أدخل نص التفريغ...',
            }),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('answer_text', 'internal_notes')
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'اكتب الإجابة هنا...',
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'ملاحظات داخلية (اختياري)...',
            }),
        }


class InquiryFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'بحث...',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'جميع الحالات')] + list(Inquiry.Status.choices),
        widget=forms.Select(attrs={
            'class': 'input select',
        }),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'جميع الأولويات')] + list(Inquiry.Priority.choices),
        widget=forms.Select(attrs={
            'class': 'input select',
        }),
    )


class GlossaryTermForm(forms.ModelForm):
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
                'rows': 5,
                'placeholder': 'التعريف...',
            }),
            'pronunciation_hint': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'تلميح النطق (اختياري)',
            }),
            'category': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'التصنيف (اختياري)',
            }),
        }
