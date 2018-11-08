from django.db import migrations

from dictionary import models
import dictionary.sql_views as sql_views


class Migration(migrations.Migration):

	dependencies = [
		('dictionary', '0003_auto_20181105_1359'),
	]

	operations = [
		migrations.RunSQL(sql_views.base_word_definitions()),
		migrations.RunSQL(sql_views.base_word_synonyms()),
		migrations.RunSQL(sql_views.base_word_antonyms()),
	]
