from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0001_initial'),
        ('schools', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=20)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('gender', models.CharField(blank=True, default='', max_length=10)),
                ('blood_group', models.CharField(blank=True, max_length=5, null=True)),
                ('address', models.TextField(blank=True, default='')),
                ('admission_date', models.DateField(null=True, blank=True)),
                ('emergency_contact', models.CharField(blank=True, default='', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('current_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='classes.class')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parents.parent')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schools.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('school', 'student_id')},
            },
        ),
    ]
