from bs4 import BeautifulSoup
import urllib.request as urllib2
import time
import random
import os
import re
from dictionary import models
from django.db import transaction


def _load_word_list(filename):
    """Reads file of words into list"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


@transaction.atomic()
def scrape_word(word):
    """Scrape entry for page and loads into database"""
    url = 'https://www.merriam-webster.com/dictionary/' + word
    r = urllib2.urlopen(url).read()
    soup = BeautifulSoup(r, 'html5lib')
    def_wrapper = soup.find('div', {'id': 'definition-wrapper'})
    left_content = def_wrapper.find('div', {'id' : 'left-content'})
    entries = (left_content.find_all('div', {'class': 'entry-header'},
               recursive=False))
    i = 1
    #Loop through all definition sections, broken down by part of speech
    for entry in entries:
        word_name = entry.find('div').find(['h1', 'p'], {'class' : 'hword'}) \
                         .getText()
        base_word_, _ = models.BaseWord.objects.get_or_create(name=word_name)
        def_entry_num = 'dictionary-entry-' + str(i)
        def_entry = left_content.find('div', {'id' :  def_entry_num})
        definitions = def_entry.find_all('span', {'class' : 'dtText'})
        try:
            pos_text = _clean_pos_text(entry
                           .find('a', {'class' : 'important-blue-link'})
                           .getText())
        except AttributeError:
            pos_text = _clean_pos_text(entry.find('span' , {'class' : 'fl'})
                                       .getText())
        pos_, _ = models.PartOfSpeech.objects.get_or_create(name=pos_text)
        form_word_, _ = (models.FormWord.objects
                                        .get_or_create(pos=pos_,
                                                       base_word=base_word_,))
        for definition in definitions:
            #These are examples or quotes we don't need in the definition
            extra_text = definition.find_all('span', {'class' : 'ex-sent'})
            clean_defs = _clean_definition(definition, extra_text)
            for clean_def in clean_defs:
                _, _ = models.WordDefinition.objects \
                             .get_or_create(form_word=form_word_,
                                            definition=clean_def)
        i += 1
    alternate_forms = left_content.find_all('span', {'class' : 'vg-ins'})
    different_spellings = set()
    different_spellings.add(word_name)
    for alternate_form in alternate_forms:
         different_forms = alternate_form.find_all('span', {'class' : 'if'})
         for different_form in different_forms:
             different_spellings.add(different_form.getText().strip())
    for spelling in different_spellings:
        _, _ = (models.VariantWord.objects.get_or_create(base_word=base_word_,
                                                         name=spelling))


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
    p = re.compile('(\w[\w ,-\\\/()]*)')
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
    for word in word_list:
        print(word)
        scrape_word(word)
        time.sleep(1)
