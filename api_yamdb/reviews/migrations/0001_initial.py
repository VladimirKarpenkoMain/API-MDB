# Generated by Django 3.2 on 2024-02-12 13:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256, verbose_name='Категория')),
                ('slug', models.SlugField(unique=True, validators=[django.core.validators.RegexValidator(message='Slug категории содержит недопустимый символ', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('name',),
            },
        ),
    ]
