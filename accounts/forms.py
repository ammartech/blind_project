from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class LoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول"""
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'اسم المستخدم',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'كلمة المرور',
        })
    )


class RegisterForm(UserCreationForm):
    """نموذج التسجيل - الحقول الأساسية مطلوبة، والباقي اختياري"""

    # Required fields
    role = forms.ChoiceField(
        label='نوع الحساب *',
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'input select'})
    )
    email = forms.EmailField(
        label='البريد الإلكتروني *',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'placeholder': 'example@email.com',
        })
    )

    # Optional fields (can be filled later)
    full_name_ar = forms.CharField(
        label='الاسم الكامل بالعربية',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'مثال: أحمد محمد علي',
        })
    )
    gender = forms.ChoiceField(
        label='الجنس',
        required=False,
        choices=[('', 'اختر...')] + list(User.Gender.choices),
        widget=forms.Select(attrs={'class': 'input select'})
    )
    phone = forms.CharField(
        label='رقم الهاتف',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'مثال: 0501234567',
            'dir': 'ltr',
        })
    )
    birth_date = forms.DateField(
        label='تاريخ الميلاد',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'input',
            'type': 'date',
        })
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'password1', 'password2',
            'full_name_ar', 'gender', 'phone', 'birth_date'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديث الحقول الأساسية
        self.fields['username'].widget.attrs.update({
            'class': 'input',
            'placeholder': 'اسم المستخدم',
        })
        self.fields['username'].label = 'اسم المستخدم *'
        self.fields['password1'].widget.attrs.update({
            'class': 'input',
            'placeholder': 'كلمة المرور',
        })
        self.fields['password1'].label = 'كلمة المرور *'
        self.fields['password2'].widget.attrs.update({
            'class': 'input',
            'placeholder': 'تأكيد كلمة المرور',
        })
        self.fields['password2'].label = 'تأكيد كلمة المرور *'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مسجل بالفعل.')
        return email


class ProfileEditForm(forms.ModelForm):
    """نموذج تعديل الملف الشخصي"""

    class Meta:
        model = User
        fields = (
            'full_name_ar', 'email', 'gender', 'phone',
            'birth_date', 'bio', 'avatar', 'receive_notifications'
        )
        widgets = {
            'full_name_ar': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'الاسم الكامل بالعربية',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'البريد الإلكتروني',
            }),
            'gender': forms.Select(attrs={
                'class': 'input select',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'رقم الهاتف',
                'dir': 'ltr',
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'اكتب نبذة قصيرة عن نفسك...',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'input-file',
                'accept': 'image/*',
            }),
            'receive_notifications': forms.CheckboxInput(attrs={
                'class': 'checkbox',
            }),
        }
        labels = {
            'full_name_ar': 'الاسم الكامل بالعربية',
            'email': 'البريد الإلكتروني',
            'gender': 'الجنس',
            'phone': 'رقم الهاتف',
            'birth_date': 'تاريخ الميلاد',
            'bio': 'نبذة شخصية',
            'avatar': 'الصورة الشخصية',
            'receive_notifications': 'استلام الإشعارات بالبريد',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم من حساب آخر.')
        return email


class ChangePasswordForm(forms.Form):
    """نموذج تغيير كلمة المرور"""

    current_password = forms.CharField(
        label='كلمة المرور الحالية',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'كلمة المرور الحالية',
        })
    )
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'كلمة المرور الجديدة',
        })
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'تأكيد كلمة المرور الجديدة',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError('كلمة المرور الحالية غير صحيحة.')
        return current

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('كلمتا المرور غير متطابقتين.')
        if p1 and len(p1) < 8:
            raise forms.ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل.')
        return cleaned
