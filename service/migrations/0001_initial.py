import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان الاستفسار')),
                ('question_text', models.TextField(blank=True, default='', verbose_name='نص السؤال')),
                ('question_audio', models.FileField(blank=True, null=True, upload_to='inquiry_audio/%Y/%m/', verbose_name='تسجيل صوتي')),
                ('transcription_text', models.TextField(blank=True, default='', verbose_name='نص التفريغ')),
                ('answer_text', models.TextField(blank=True, default='', verbose_name='نص الإجابة')),
                ('answered_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإجابة')),
                ('status', models.CharField(choices=[('new', 'جديد'), ('transcribed', 'تم التفريغ'), ('in_progress', 'قيد المعالجة'), ('answered', 'تمت الإجابة'), ('closed', 'مغلق')], default='new', max_length=20, verbose_name='الحالة')),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('normal', 'عادية'), ('high', 'عالية'), ('urgent', 'عاجلة')], default='normal', max_length=20, verbose_name='الأولوية')),
                ('is_read_by_user', models.BooleanField(default=False)),
                ('is_read_by_librarian', models.BooleanField(default=False)),
                ('internal_notes', models.TextField(blank=True, default='', verbose_name='ملاحظات داخلية')),
                ('answered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='answered_inquiries', to=settings.AUTH_USER_MODEL, verbose_name='أجاب عليه')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to=settings.AUTH_USER_MODEL, verbose_name='المستفسر')),
            ],
            options={
                'verbose_name': 'استفسار',
                'verbose_name_plural': 'الاستفسارات',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GlossaryTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=200, verbose_name='المصطلح')),
                ('definition', models.TextField(verbose_name='التعريف')),
                ('pronunciation_hint', models.CharField(blank=True, default='', max_length=300, verbose_name='تلميح النطق')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='عدد المشاهدات')),
                ('tts_play_count', models.PositiveIntegerField(default=0, verbose_name='مرات القراءة الصوتية')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='glossary_terms', to=settings.AUTH_USER_MODEL, verbose_name='أضافه')),
            ],
            options={
                'verbose_name': 'مصطلح',
                'verbose_name_plural': 'المصطلحات',
                'ordering': ['term'],
            },
        ),
    ]
