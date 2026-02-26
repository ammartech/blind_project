from django.conf import settings
from django.db import models


class GlossaryCategory(models.Model):
    """تصنيف مصطلحات القاموس"""
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم التصنيف')
    description = models.TextField(blank=True, default='', verbose_name='وصف التصنيف')
    icon = models.CharField(max_length=10, blank=True, default='', verbose_name='أيقونة')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def term_count(self):
        return self.terms.count()


class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'جديد'
        TRANSCRIBED = 'transcribed', 'تم التفريغ'
        IN_PROGRESS = 'in_progress', 'قيد المعالجة'
        ANSWERED = 'answered', 'تمت الإجابة'
        CLOSED = 'closed', 'مغلق'

    class Priority(models.TextChoices):
        LOW = 'low', 'منخفضة'
        NORMAL = 'normal', 'عادية'
        HIGH = 'high', 'عالية'
        URGENT = 'urgent', 'عاجلة'

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    title = models.CharField(max_length=200, verbose_name='عنوان الاستفسار')
    question_text = models.TextField(blank=True, default='', verbose_name='نص السؤال')
    question_audio = models.FileField(
        upload_to='inquiry_audio/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='تسجيل صوتي',
    )
    transcription_text = models.TextField(blank=True, default='', verbose_name='نص التفريغ')
    answer_text = models.TextField(blank=True, default='', verbose_name='نص الإجابة')
    answered_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإجابة')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='الحالة',
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        verbose_name='الأولوية',
    )
    is_read_by_user = models.BooleanField(default=False)
    is_read_by_librarian = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True, default='', verbose_name='ملاحظات داخلية')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inquiries',
        verbose_name='المستفسر',
    )
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answered_inquiries',
        verbose_name='أجاب عليه',
    )

    class Meta:
        verbose_name = 'استفسار'
        verbose_name_plural = 'الاستفسارات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=200, verbose_name='المصطلح')
    definition = models.TextField(verbose_name='التعريف')
    pronunciation_hint = models.CharField(
        max_length=300, blank=True, default='', verbose_name='تلميح النطق'
    )
    category = models.ForeignKey(
        GlossaryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='terms',
        verbose_name='التصنيف',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    view_count = models.PositiveIntegerField(default=0, verbose_name='عدد المشاهدات')
    tts_play_count = models.PositiveIntegerField(default=0, verbose_name='مرات القراءة الصوتية')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='glossary_terms',
        verbose_name='أضافه',
    )

    class Meta:
        verbose_name = 'مصطلح'
        verbose_name_plural = 'المصطلحات'
        ordering = ['term']

    def __str__(self):
        return self.term

    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
