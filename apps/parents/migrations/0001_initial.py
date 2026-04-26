from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, default='', max_length=20)),
                ('occupation', models.CharField(blank=True, max_length=100, null=True)),
                ('relationship', models.CharField(
                    choices=[('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')],
                    default='guardian', max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='schools.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
