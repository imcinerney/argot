from bs4 import BeautifulSoup
import requests
import time
import random
import os
import re
from dictionary import models
from django.db import transaction
from django.db.models import F


def _load_word_list(filename):
    """Reads file of words into list"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


@transaction.atomic()
def scrape_word(word, search_synonym=False):
    """Scrape entry for page and loads into database

    Keyword arguments:
    word -- word to add to database
    search_synonym -- boolean to add all synonyms listed to database as well
    use_links -- boolean to signal whether the word being passed is a link or
    just the word
    """
    url = 'https://www.merriam-webster.com/dictionary/' + word
    r = requests.get(url)
    print('The status code of the request is: {0}'.format(r.status_code))
    soup = BeautifulSoup(r.content, 'html5lib')
    def_wrapper = soup.find('div', {'id': 'definition-wrapper'})
    left_content = def_wrapper.find('div', {'id' : 'left-content'})
    #separate function to reduce size of function
    (word_name, base_word_) = \
        _add_base_form_def_pos_example_to_db(left_content)
    #Add different spellings of word to model
    alternate_forms = left_content.find_all('span', {'class' : 'vg-ins'})
    different_spellings = set()
    different_spellings.add(word_name)
    different_spellings.add(word)
    for alternate_form in alternate_forms:
         different_forms = alternate_form.find_all('span', {'class' : 'if'})
         for different_form in different_forms:
             different_spellings.add(different_form.getText().strip())
    for spelling in different_spellings:
        _, _ = (models.VariantWord.objects.get_or_create(base_word=base_word_,
                                                         name=spelling))
    if search_synonym:
        _add_synonyms(left_content, base_word_)


def _add_synonyms(left_content, base_word_):
    """Adds synonyms to database

    Keyword arguments:
    left_content -- the portion of the merriam-webster webpage that stores the
    pertinent information for building our entry
    base_word_ -- BaseWord object associated with the word we are looking up

    Adds synonyms listed on page, checks to see if words are in database,
    if they are not, call scrape_word() to add them and then add to database.

    The large issue with getting synonyms on Merriam-Webster is that sometimes
    Merriam-Webster's entry for a word does not have the synonym/antonym section
    that most entries do. However, there's another section that contains a list
    of synonyms. _scrape_synonym_section() handles the default synonym section,
    while _scrape_alternative_synonym_section() handles the alternative synonym
    section. They return a list that contains a tuple that stores the part of
    speech and then a list of words to add to the dictionary and synonym table.
    Synonyms are tied to the part of speech of a word.
    """
    try:
        pos_synonym_list = _scrape_synonym_section(left_content)
    except AttributeError:
        try:
            pos_synonym_list = _scrape_alternative_synonym_section(left_content)
        except AttributeError:
            return
    pos_list = models.PartOfSpeech.objects.all().values_list('name', flat=True)
    for synonym_pos, word_list in pos_synonym_list:
        synonym_flag, pos = _separate_synonym_pos(synonym_pos, base_word_)
        lookup_form_word = _return_form_word(pos, base_word_.name)
        for word in word_list:
            variant_word_set = models.VariantWord.objects.values_list('name',
            flat=True)
            p = re.compile('(^[a-z\-]*)')
            m = p.match(word.getText().lower())
            word_text = m.group(1)
            if word_text not in variant_word_set:
                time.sleep(2)
                print('looking up the synonym: {0}'.format(word_text))
                scrape_word(word_text)
            synonym_base_word = _return_base_word(word_text)
            if synonym_flag == 'synonyms':
                _, _ = models.Synonym.objects \
                             .get_or_create(base_word=lookup_form_word,
                                            synonym=synonym_base_word)
            else:
                _, _ = models.Antonym.objects \
                             .get_or_create(base_word=lookup_form_word,
                                            antonym=synonym_base_word)


def _return_base_word(word):
    """Looks up a word in the variant word table and returns the baseword"""
    bw = models.VariantWord.objects.all().get(name=word).base_word
    return bw


def _separate_synonym_pos(synonym_pos, base_word_):
    """Returns whether or not the words are synonyms or antonyms and the pos"""
    pos_list = models.PartOfSpeech.objects.all().values_list('name', flat=True)
    #Check if there is no part of speech listed
    if synonym_pos in ['antonyms', 'synonyms']:
        word_pos = base_word_.return_pos_list()
        if len(word_pos) != 1:
            raise ValueError('There is more than one part of speech for a '
                             'word but the synonym list does not list '
                             'synonyms in the format we expected. Look at '
                             'the page for {0}'
                             .format(base_word.name))
        else:
           return (synonym_pos, word_pos[0])
    else:
        for pos in pos_list:
            regex_pattern = '(synonyms|antonyms)[: ]*(' + pos + ')'
            p = re.compile(regex_pattern)
            match = p.search(synonym_pos)
            if match is not None:
                return (match.group(1), match.group(2))
        #If it hasn't returned, means that there must be issue
        raise ValueError('The synonym string did not meet the expected pattern'
                         '\nThe description was {0}'.format(synonym_pos))


def _return_form_word(pos, base_word_):
    """Returns the form word object for a given base word and pos"""
    fw = models.FormWord.objects.annotate(bw=F('base_word__name')) \
                                .annotate(pos_n=F('pos__name')) \
                                .get(bw=base_word_, pos_n=pos)
    return fw


def _scrape_synonym_section(left_content):
    """Scrapes the default synonym section for a word. If there is no pos
    listed, use the one listed for the word
    """
    synonym_header = left_content.find('div',
                                      {'class' : 'synonyms_list'})
    synonym_labels = synonym_header.find_all('p',
                                            {'class' : 'function-label'})
    synonym_lists = synonym_header.find_all('p', {'class' : None})
    if len(synonym_labels) != len(synonym_lists):
        raise ValueError('there are an uneven number of labels and lists')
    pos_synonym_list = []
    for label, s_list in zip(synonym_labels, synonym_lists):
        word_list = s_list.find_all('a')
        word_list_text = [word for word in word_list]
        pos = label.getText().lower()
        pos_synonym_list.append((pos, word_list_text))
    return pos_synonym_list


def _scrape_alternative_synonym_section(left_content):
    """Scrapes the alternative synonym listing"""
    #always going to have synonyms under this header
    synonym_header = left_content.find('div',
                                      {'class' : 'syns_discussion'})
    synonym_lists = synonym_header.find_all('p', {'class' : 'syn'})
    synonym_labels = synonym_header.find_all('p', {'class' : None})
    #If there is no pos listed, use the pos of the word
    if len(synonym_labels) == 0:
        if len(synonym_lists) > 1:
            raise ValueError('More than 1 synonym lists, but no pos listed')
        pos_name = 'synonyms'
        word_list = synonym_lists[0].find_all('a')
        word_list_text = [word for word in word_list]
        pos_synonym_list = [(pos_name, word_list_text)]
    else:
        pos_synonym_list = []
        for label, s_list in zip(synonym_labels, synonym_lists):
            word_list = s_list.find_all('a')
            word_list_text = [word for word in word_list]
            pos = 'synonyms: ' + label.getText().lower()
            pos_synonym_list.append((pos, word_list_text))
    return pos_synonym_list


def _add_base_form_def_pos_example_to_db(left_content):
    """Adds BaseWord, PartOfSpeech, FormWord, and WordDefinition to db"""
    entries = (left_content.find_all('div', {'class': 'entry-header'},
               recursive=False))
    i = 1
    variant_word_set = models.VariantWord.objects.all().values_list('name',
                                                                    flat=True)
    #Loop through all definition sections, broken down by part of speech
    for entry in entries:
        word_name = entry.find('div').find(['h1', 'p'], {'class' : 'hword'}) \
                         .getText().lower()
        #If we already have the word name in the dictionary, then return base
        if word_name in variant_word_set:
            base_word_, _ = models.BaseWord.objects \
                                  .get_or_create(name=word_name)
            return (word_name, base_word_)
        base_word_, _ = models.BaseWord.objects.get_or_create(name=word_name)
        def_entry_num = 'dictionary-entry-' + str(i)
        def_entry = left_content.find('div', {'id' :  def_entry_num})
        definitions = def_entry.find_all('span', {'class' : 'dtText'})
        try:
            pos_text = _clean_pos_text(entry
                           .find('a', {'class' : 'important-blue-link'})
                           .getText())
        except AttributeError:
            try:
                pos_text = _clean_pos_text(entry.find('span' , {'class' : 'fl'})
                                           .getText())
            except AttributeError:
                continue
        pos_, _ = models.PartOfSpeech.objects.get_or_create(name=pos_text)
        form_word_, _ = (models.FormWord.objects
                                        .get_or_create(pos=pos_,
                                                       base_word=base_word_,))
        for definition in definitions:
            #These are examples or quotes we don't need in the definition
            extra_text = definition.find_all('span', {'class' : 'ex-sent'})
            examples = definition.find_all('span', {'class' : 't'})
            clean_defs = _clean_definition(definition, extra_text)
            for clean_def in clean_defs:
                word_def, _ = models.WordDefinition.objects \
                                    .get_or_create(form_word=form_word_,
                                                   definition=clean_def)
                for example in examples:
                    example_text = _clean_example_text(example.getText())
                    _, _ = models.ExampleSentence.objects \
                                 .get_or_create(definition=word_def,
                                                sentence=example_text)
        i += 1
    return (word_name, base_word_)


def _clean_example_text(example_text):
    """Returns just a sentence"""
    p = re.compile('([A-z][A-z ,-\\\/()]*)')
    match = p.search(example_text)
    if match is None:
        raise (ValueError('Something wrong happened when extracting the part '
                          'of speech. The extracted text is: {0}'
                          .format(example_text)))
    return match.group()


def _clean_definition(definition, extra_text):
    """Clean a scraped definition"""
    def_text = definition.getText().strip()
    for text in extra_text:
        extra = text.getText().strip()
        def_text = def_text.replace(extra, '')
    #sometimes multiple definition appear on one line
    def_text = def_text.replace('archaic :', 'archaic --')
    def_text = re.sub('\(see.*', '', def_text)
    def_text = re.sub('sense [0-9]', '', def_text)
    split_defs = def_text.split(':')
    p = re.compile('([a-zA-Z][a-zA-Z ,-\\\/()]*)')
    return [p.search(split_def).group()
            for split_def in split_defs
            if p.search(split_def) is not None]


def _clean_pos_text(pos_text):
    """Limit to just the word"""
    p = re.compile('([A-z]*)')
    match = p.search(pos_text)
    if match.group() is None:
        raise (ValueError('Something wrong happened when extracting the part '
                          'of speech. The extracted text is: {0}'
                          .format(pos_text)))
    else:
        return match.group()


def load_list_of_words(filename):
    """Loads list of words, looks up each entry, and loads information
    into database.
    """
    word_list_file = os.path.join('dictionary', 'word_lists', filename)
    word_list = _load_word_list(word_list_file)
    variant_word_set = models.VariantWord.objects.values_list('name', flat=True)
    for word in word_list:
        if word not in variant_word_set:
            print(word)
            scrape_word(word, search_synonym=True)
            time.sleep(1)
