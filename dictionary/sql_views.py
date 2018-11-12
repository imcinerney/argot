from dictionary import models
from django.db.models import F, Count, Subquery, OuterRef
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
    subq1 = (models.BaseWord.objects.all()
                 .filter(id=OuterRef('id'))
                 .annotate(pos_count=Count('formword__pos__name'))
          )
    subq2 = (models.BaseWord.objects.all()
                 .filter(id=OuterRef('id'))
                 .annotate(synonym_count=
                    Count('formword__synonym__synonym__name'))
          )
    subq3 = (models.BaseWord.objects.all()
                 .filter(id=OuterRef('id'))
                 .annotate(antonym_count=
                    Count('formword__antonym__antonym__name'))
          )
    qs = (models.BaseWord.objects.all()
                .order_by('id')
                .annotate(pos_count=Subquery(subq1.values('pos_count')))
                .annotate(synonym_count=Subquery(subq2.values('synonym_count')))
                .annotate(antonym_count=Subquery(subq3.values('antonym_count')))
        )
    sql_statement = 'create view base_word_stats as ' + str(qs.query)
    return sql_statement


def _export_views(view_name):
    """Used for debugging purposes, generates a query to test validity"""
    try:
        s = eval(view_name)()
    except NameError:
        raise NameError(f'No sql view found with the name {view_name}')
    export_file = os.path.join('dictionary', 'sql_queries', view_name + '.sql')
    with open(export_file, 'w+') as f:
        f.write(str(s))
