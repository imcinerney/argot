# Generated by Django 2.1.2 on 2018-12-10 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0011_auto_20181210_1739'),
    ]

    operations = [
        migrations.RenameField(
            model_name='antonym',
            old_name='form_word',
            new_name='base_word',
        ),
        migrations.RenameField(
            model_name='synonym',
            old_name='form_word',
            new_name='base_word',
        ),
    ]
