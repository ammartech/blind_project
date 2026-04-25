from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('blind', 'مستفيد من ذوي الإعاقة البصرية'),
                    ('librarian', 'أخصائي مكتبة'),
                ],
                default='blind',
                max_length=20,
                verbose_name='نوع الحساب',
            ),
        ),
    ]
