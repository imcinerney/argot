# Generated by Django 2.1.2 on 2018-11-28 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_sql_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseword',
            name='searched_synonym',
            field=models.BooleanField(default=False),
        ),
    ]
