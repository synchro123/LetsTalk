# Generated by Django 3.0 on 2020-09-16 16:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='status',
            field=models.TextField(default=django.utils.timezone.now, verbose_name='Статус'),
            preserve_default=False,
        ),
    ]
