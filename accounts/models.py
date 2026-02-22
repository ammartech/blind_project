from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    نموذج المستخدم المخصص مع حقول إضافية للملف الشخصي
    """

    class Role(models.TextChoices):
        BLIND = 'blind', 'مستفيد (مكفوف)'
        LIBRARIAN = 'librarian', 'أخصائي مكتبة'

    class Gender(models.TextChoices):
        MALE = 'male', 'ذكر'
        FEMALE = 'female', 'أنثى'
        PREFER_NOT_SAY = 'not_specified', 'أفضل عدم التحديد'

    # الدور (موجود مسبقاً)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BLIND,
        verbose_name='نوع الحساب'
    )

    # حقول الملف الشخصي الجديدة
    full_name_ar = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='الاسم الكامل بالعربية'
    )
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        verbose_name='الجنس'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='رقم الهاتف'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاريخ الميلاد'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='نبذة شخصية'
    )

    # الصورة الشخصية
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='الصورة الشخصية'
    )

    # التفضيلات
    receive_notifications = models.BooleanField(
        default=True,
        verbose_name='استلام الإشعارات'
    )

    # آخر تحديث للملف الشخصي
    profile_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخر تحديث للملف الشخصي'
    )

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        return self.get_display_name()

    # الدوال الموجودة مسبقاً
    def is_blind(self) -> bool:
        return self.role == self.Role.BLIND

    def is_librarian(self) -> bool:
        return self.role == self.Role.LIBRARIAN

    # دوال جديدة للملف الشخصي
    def get_display_name(self):
        """الحصول على اسم العرض"""
        if self.full_name_ar:
            return self.full_name_ar
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def get_initials(self):
        """الحصول على الأحرف الأولى للاسم"""
        name = self.get_display_name()
        if name:
            parts = name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}"
            return name[0]
        return self.username[0].upper()

    def profile_completion_percentage(self):
        """نسبة اكتمال الملف الشخصي"""
        fields = [
            self.full_name_ar,
            self.gender,
            self.phone,
            self.birth_date,
            self.bio,
            self.email,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
