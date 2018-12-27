from django.db import migrations
from django.core.management import call_command
from dictionary import models
import dictionary.sql_views as sql_views
import os


class Migration(migrations.Migration):


    def load_data(apps, schema_editor):
        fixture_file = os.path.join((os.path.dirname(__file__)), '../fixtures',
                                    'initial_data.json')
        call_command('loaddata', fixture_file)

    dependencies = [
        ('dictionary', '0017_useraccuracy'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
