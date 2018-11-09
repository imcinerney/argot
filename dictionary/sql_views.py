from dictionary import models
from django.db.models import F
import os


def base_word_definitions():
    """Lists every definition for every base word"""
    qs = (models.BaseWord.objects.all()
                .annotate(pos=F('formword__pos__name'))
                .annotate(definition=F('formword__worddefinition__definition'))
                .values('name', 'pos', 'definition')
         )
    sql_statement = 'create view definition_view as ' + str(qs.query)
    return sql_statement


def base_word_synonyms():
    """Lists every synonym for every base word"""
    qs = (models.BaseWord.objects.all()
                .annotate(pos=F('formword__pos__name'))
                .annotate(synonym_name=F('formword__synonym__synonym__name'))
                .filter(synonym_name__isnull=False)
                .values('name', 'pos', 'synonym_name')
         )
    sql_statement = 'create view synonym_list as ' + str(qs.query)
    return sql_statement


def base_word_antonyms():
    """Lists every antonym for every base word"""
    qs = (models.BaseWord.objects.all()
                .annotate(pos=F('formword__pos__name'))
                .annotate(antonym_name=F('formword__antonym__antonym__name'))
                .filter(antonym_name__isnull=False)
                .values('name', 'pos', 'antonym_name')
         )
    sql_statement = 'create view antonym_list as ' + str(qs.query)
    return sql_statement


def base_word_stats():
    """Generates count of pos, definitions, synonyms, and antonyms"""
    pass


def _export_views(view_name):
    """Used for debugging purposes, generates a query to test validity"""
    s = eval(view_name)()
    export_file = os.path.join('dictionary', 'sql_queries', view_name + '.sql')
    with open(export_file, 'w+') as f:
        f.write(str(s))
