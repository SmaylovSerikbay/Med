# Generated manually for ClinicEmployerPartnership model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0003_alter_employee_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicEmployerPartnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('active', 'Активно'), ('rejected', 'Отклонено'), ('suspended', 'Приостановлено'), ('expired', 'Истекло')], default='pending', max_length=20, verbose_name='Статус')),
                ('pricing', models.JSONField(blank=True, default=dict, verbose_name='Цены на услуги')),
                ('default_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Стандартная цена')),
                ('is_public', models.BooleanField(default=False, verbose_name='Открытая клиника (публичная)')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('requested_at', models.DateTimeField(auto_now_add=True, verbose_name='Запрошено')),
                ('confirmed_at', models.DateTimeField(blank=True, null=True, verbose_name='Подтверждено')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Действует до')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clinic', models.ForeignKey(limit_choices_to={'org_type': 'clinic'}, on_delete=django.db.models.deletion.CASCADE, related_name='employer_partnerships', to='organizations.organization', verbose_name='Клиника')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partnership_confirmations', to=settings.AUTH_USER_MODEL, verbose_name='Подтвердил')),
                ('employer', models.ForeignKey(limit_choices_to={'org_type': 'employer'}, on_delete=django.db.models.deletion.CASCADE, related_name='clinic_partnerships', to='organizations.organization', verbose_name='Работодатель')),
                ('requested_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partnership_requests', to=settings.AUTH_USER_MODEL, verbose_name='Запросил')),
            ],
            options={
                'verbose_name': 'Партнерство клиники и работодателя',
                'verbose_name_plural': 'Партнерства клиник и работодателей',
                'ordering': ['-created_at'],
                'unique_together': {('clinic', 'employer')},
            },
        ),
        migrations.AddIndex(
            model_name='clinicemployerpartnership',
            index=models.Index(fields=['clinic', 'status'], name='organizatio_clinic__idx'),
        ),
        migrations.AddIndex(
            model_name='clinicemployerpartnership',
            index=models.Index(fields=['employer', 'status'], name='organizatio_employer_idx'),
        ),
        migrations.AddIndex(
            model_name='clinicemployerpartnership',
            index=models.Index(fields=['status'], name='organizatio_status_idx'),
        ),
    ]

