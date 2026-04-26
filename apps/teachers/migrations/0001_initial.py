from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_schooluser_global_id'),
        ('classes', '0001_initial'),
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(blank=True, max_length=20, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(blank=True, max_length=30, null=True)),
                ('qualification', models.CharField(blank=True, max_length=200, null=True)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='schools.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_profile', to='accounts.schooluser')),
            ],
            options={
                'unique_together': {('school', 'employee_id')},
            },
        ),
        migrations.CreateModel(
            name='TeacherSchoolAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_assignments', to='teachers.teacher')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='schools.school')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='teachers.subject')),
                ('assigned_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_assignments', to='classes.class')),
            ],
            options={
                'ordering': ['school', 'subject'],
                'unique_together': {('teacher', 'school', 'subject', 'assigned_class')},
            },
        ),
    ]
