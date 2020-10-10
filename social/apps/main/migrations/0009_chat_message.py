# Generated by Django 3.0 on 2020-09-29 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0008_auto_20200923_2137'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название чата')),
                ('private_chat', models.BooleanField(default=True, verbose_name='Является ли чат приватным')),
                ('dialog', models.BooleanField(default=True, verbose_name='Чат на двух людей (Диалог)')),
                ('members', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('writing_people', models.ManyToManyField(blank=True, related_name='i_writing', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='текст сообщения')),
                ('write_date', models.DateTimeField(auto_now=True, verbose_name='время оставления')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Chat')),
            ],
        ),
    ]
