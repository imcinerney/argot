"""This module handles scraping dictionary entries and adding them to the db

This module handles visiting a website to look up a word's definition and then
navigating the HTML to extract the desired information to store in the database.

Main Functions:
    scrape_word(word, search_synonym=False)
        word: string of word to lookup
        search_synonym: boolean indicating whether or not to look up the
        synonyms listed for a word, if set false this information is stored in
        a table for a later lookup

        This function is the main function of the module, it handles looking up
        a word and storing it in the databse. The function will check to make
        sure that the word already isn't in the database. It returns True if
        the word entered had a valid entry, returns False if the site didn't
        match a word.

        Example:
            python3 manage.py shell
            from dictionary import merriam_webster_scraper as mws
            mws.scrape_word('bolster', True)

    load_list_of_words(filename)
        filename: name of file to lookup stored in dictionary/word_lists/

        Scraped the definition of every word in the file. Each line should be a
        word to lookup. The default search_synonym for this words is True,
        meaning that the scraper will visit the entry pages for every
        synonym and antonym listed on the page. Easy way to fill the database
        with a lot of entries at once.

        Example:
            python3 manage.py shell
            from dictionary import merriam_webster_scraper as mws
            mws.load_list_of_words('top_gre_words.txt')

    fill_in_synonyms()
        This function will look at all of the synonyms for the base words whose
        synonyms we have not added yet. Depending on how many words are in the
        database, this function could take a while to complete. Fills in
        incompete entries.

        Example:
            python3 manage.py shell
            from dictionary import merriam_webster_scraper as mws
            mws.fill_in_synonyms()
"""

from bs4 import BeautifulSoup
import requests
import time
import random
import os
import re
from dictionary import models
from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError


@transaction.atomic()
def scrape_word(word, search_synonym=False):
    """Scrape entry for page and loads into database

    Keyword arguments:
    word -- word to add to database
    search_synonym -- boolean to add all synonyms listed to database as well

    Returns True if word found, False if not
    """
    if _already_entered(word, search_synonym):
        return True
    url = 'https://www.merriam-webster.com/dictionary/' + word
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        time.sleep(5)
        return scrape_word(word, search_synonym)
    if r.status_code == 404:
        return False
    soup = BeautifulSoup(r.content, 'html5lib')
    _manage_dictionary_entries(soup, word, search_synonym)
    return True


def load_list_of_words(filename):
    """Loads list of words and adds to db if not already in"""
    word_list_file = os.path.join('dictionary', 'word_lists', filename)
    word_list = _load_word_list(word_list_file)
    variant_word_set = models.VariantWord.objects.values_list('name', flat=True)
    for word in word_list:
        if word not in variant_word_set:
            print(word)
            scrape_word(word, search_synonym=True)
            time.sleep(1)


def fill_in_synonyms():
    """Adds the synonyms for all basewords that haven't been added yet"""
    qs = models.BaseWord.objects.filter(searched_synonym=False)
    for word in qs:
        print(word.name)
        scrape_word(word.name, search_synonym=True)
        time.sleep(2)


def _already_entered(word, search_synonym):
    """Checks to see if a word is already entered.

    If a word has been entered, check if the synonyms have been searched. If
    they haven't and search_synonym is true, then lookup all of the words
    associated with the baseword in the SynonymsToLookUp table
    """
    variant_word_set = models.VariantWord.objects.all().values_list('name',
                                                                    flat=True)
    if word in variant_word_set:
        if search_synonym:
            base_word_ = models.VariantWord.objects.get(name=word).base_word
            if not base_word_.searched_synonym:
                synonyms_to_lookup = base_word_.synonymstolookup_set.all()
                for synonym in synonyms_to_lookup:
                    if synonym.is_synonym:
                        print(f'Looking up the synonym: {synonym.lookup_word}')
                    else:
                        print(f'Looking up the antonym: {synonym.lookup_word}')
                    valid_word = scrape_word(synonym.lookup_word)
                    synonym_word = synonym.lookup_word
                    if valid_word:
                        synonym_vw = models.VariantWord.objects \
                                                       .get(name=synonym_word)
                        if synonym.is_synonym:
                            _ = models.Synonym.objects \
                                      .get_or_create(base_word=base_word_,
                                                     synonym=synonym_vw)
                        else:
                            _ = models.Antonym.objects \
                                      .get_or_create(base_word=base_word_,
                                                     antonym=synonym_vw)
                    synonym.delete()
                base_word_.searched_synonym = True
                base_word_.save()
        return True
    else:
        return False


def _manage_dictionary_entries(soup, word, search_synonym):
    """Searches soup for pertinent sections and sends to functions to handle"""
    def_wrapper = soup.find('div', {'id': 'definition-wrapper'})
    left_content = def_wrapper.find('div', {'id' : 'left-content'})
    #If there's an entry, probably a more commonly spelled name to search
    first_entry = left_content.find('div', {'id' : 'dictionary-entry-1'})
    new_word = first_entry.find('a', {'class' : 'cxt', 'rel' : 'prev'})
    if new_word is not None:
        time.sleep(1)
        new_word = new_word.getText().strip()
        print(f'revising search from {word} to {new_word}')
        return scrape_word(new_word, search_synonym)
    variant_word_set = models.VariantWord.objects.all().values_list('name',
                                                                    flat=True)
    (word_name, base_word_) = _handle_main_dictionary_entry(left_content,
                                                            variant_word_set,
                                                            search_synonym)
    if base_word_ is None:
        return None
    _compile_alternate_spellings(left_content, word_name, word, base_word_,
                                 variant_word_set)
    _add_synonyms(left_content, base_word_, search_synonym)


def _handle_main_dictionary_entry(left_content, variant_word_set,
                                  search_synonym):
    """Searches for content containing the main aspects of a dictionary entry

    Keyword argument:
    left_content -- section of wepage containing the text of the dictionary
    entries
    variant_word_set -- list of all spellings of words currently in the
    database
    search_synonym -- whether or not we will search for synonyms for the word

    Loops through the main sections of the webpage. Will create the base_word,
    form_words, the definitions, pos, examples for a word
    """
    entries = (left_content.find_all('div', {'class': 'entry-header'},
               recursive=False))
    i = 1
    first_entry = entries[0]
    remaining_entries = entries[1:]
    (base_word_, word_name) = _add_base_and_form(first_entry,
                                                  i, left_content,
                                                  variant_word_set,
                                                  search_synonym)
    #Loop through all definition sections, broken down by part of speech
    for entry in remaining_entries:
        i += 1
        #We only use the return values for the first entry
        if base_word_ is not None:
            _ = _add_base_and_form(entry, i, left_content,
                                   variant_word_set, search_synonym)
        else:
            (base_word_, _) = _add_base_and_form(entry, i, left_content,
                                                    variant_word_set,
                                                    search_synonym)
    return (word_name, base_word_)


def _add_base_and_form(entry, i, left_content, variant_word_set,
                       search_synonym):
    """Function to add baseword and formword entries to db

    Keyword arguments:
    entry -- section of page that contains information on the word name and
    part of speech
    i -- used to identify which section the corresponding defintion and example
    is located
    left_content -- main section that contains all information on the entries
    for words
    variant_word_set -- list of all spellings of words currently in the
    database
    search_synonym -- whether or not we will search for synonyms for the word

    Returns:
    (base_word_, word_name)
    base_word_ -- BaseWord object for the dictionary page
    word_name -- The word_name as appears on the webpage (could be diff from
    what gets searched)
    """
    word_name = entry.find('div').find(['h1', 'p'], {'class' : 'hword'}) \
                     .getText().lower()
    word_name = _clean_word_name(word_name)
    if word_name is None:
        return (None, None)
    base_word_, _ = models.BaseWord.objects.get_or_create(name=word_name,
                        searched_synonym=search_synonym)
    pos_ = _find_pos(entry)
    #If there's no pos, probably not a valid dictionary entry
    if pos_ is None:
        return (None, word_name)
    form_word_, _ = (models.FormWord.objects
                                    .get_or_create(pos=pos_,
                                                   base_word=base_word_,))
    _add_definition_and_examples(i, left_content, form_word_)
    return (base_word_, word_name)


def _add_definition_and_examples(dictionary_entry_num, left_content,
                                 form_word_):
    """Helper function to find the defintion & example sentence sections

    Keyword arguments:
    dictionary_entry_num -- Used to locate the correct HTML tag
    left_content -- The part of the webpage that contains all pertinent info
    form_word_ -- FormWord object to link definition to

    Merriam webster does not keep all information for an entry in one parent
    HTML tag. Instead, it puts information regarding the word name and part of
    speech in one tag and then another tag for the defintions and example
    sentence in the next tag. We use the dictionary_entry_num to locate the
    associated definition entry with the correct word and pos.

    Returns nothing, as we just create the entries unless they are already in
    the database.
    """
    def_entry_num = 'dictionary-entry-' + str(dictionary_entry_num)
    def_entry = left_content.find('div', {'id' :  def_entry_num})
    definition_headers = def_entry.find_all('div', {'class' : 'vg'},
                                            recursive=False)
    for def_header in definition_headers:
        definitions = def_header.find_all('span', {'class' : 'dtText'})
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


def _find_pos(entry):
    """Helper function to find the pos on the site and return pos object

    Keyword arguments:
    entry -- the section of HTML that contains word_name, def, and pos

    The part of speech can be found in different sections. Most of the time it
    it stored in the 'import-blue-link' class within the entry. Otherwise, it
    is in the 'fl' class. If it isn't in either of those, return a None. If it
    is found, returns a PartOfSpeech object.
    """
    try:
        pos_text = _clean_pos_text(entry
                       .find('a', {'class' : 'important-blue-link'})
                       .getText())
    except AttributeError:
        try:
            pos_text = _clean_pos_text(entry.find('span' , {'class' : 'fl'})
                                       .getText())
        except AttributeError:
            return None
    pos_, _ = models.PartOfSpeech.objects.get_or_create(name=pos_text)
    return pos_


def _clean_example_text(example_text):
    """Returns just a sentence"""
    p = re.compile('([A-z][A-z ,-\\\/()\']*)')
    match = p.search(example_text)
    if match is None:
        raise (ValueError(f'Something wrong happened when extracting the part '
                          f'of speech. The extracted text is: {example_text}'))
    return match.group()


def _clean_definition(definition, extra_text):
    """Clean a scraped definition"""
    def_text = definition.getText().strip()
    for text in extra_text:
        extra = text.getText().strip()
        def_text = def_text.replace(extra, '')
    def_text = def_text.replace('archaic :', 'archaic --')
    def_text = re.sub('\(see.*\)', '', def_text)
    def_text = re.sub('sense [0-9][a-zA-Z]?', '', def_text)
    def_text = re.sub('sense [a-zA-Z]?', '', def_text)
    def_text = re.sub(' +', ' ', def_text)
    split_defs = def_text.split(':')
    p = re.compile('([a-zA-Z][a-zA-Z ,-\\\/()\']*)')
    return [p.search(split_def).group().strip()
            for split_def in split_defs
            if p.search(split_def) is not None]


def _clean_pos_text(pos_text):
    """Limit to just the word"""
    p = re.compile('([A-z ]*)')
    match = p.search(pos_text)
    if match.group() is None:
        raise (ValueError(f'Something wrong happened when extracting the part '
                          f'of speech. The extracted text is: {pos_text}'))
    else:
        return match.group().strip()


def _clean_word_name(word):
    """Cleans the text for a word name, returns None if no match

    Prevents us from adding entries that are just prefixes of suffixes, e.g.
    -phobia.
    """
    p = re.compile('(^[\w]+[\w-]*[\w]+)')
    match = p.search(word)
    if match is None:
        #Make sure we aren't excluding one letter words
        p = re.compile('(^[\w]$)')
        match = p.search(word)
        if match is None:
            return None
        else:
            return match.group(0)
    else:
        return match.group(0)


def _compile_alternate_spellings(left_content, word_name, word, base_word_,
                             variant_word_set):
    """Search the page to add all the alternatative spellings of a word

    Merriam webster sometimes stores this info in two parts, thus the adding
    of the words in 'variants' section an dalso the 'alternate_forms' sections
    """
    alternate_forms = left_content.find_all('span', {'class' : 'vg-ins'})
    variants = left_content.find_all('a', {'class' : 'va-link'})
    other_word_section = left_content.find('div', {'id' : 'other-words-anchor'})
    if other_word_section:
        other_words = other_word_section.find_all('div', {'class' : 'uro'})
    else:
        other_words = []
    different_spellings = set()
    different_spellings.add(word_name)
    different_spellings.add(word)
    for variant in variants:
        different_spellings.add(variant.getText().strip())
    for alternate_form in alternate_forms:
         different_forms = alternate_form.find_all('span', {'class' : 'if'})
         for different_form in different_forms:
             different_spellings.add(different_form.getText().strip())
    for other_word in other_words:
        different_spellings.add(other_word.find('span', {'class' : 'ure'})
                                          .getText().strip())
    different_spellings = [spelling for spelling in different_spellings
                           if spelling not in variant_word_set]
    for spelling in different_spellings:
        _, _ = (models.VariantWord.objects.get_or_create(base_word=base_word_,
                                                         name=spelling))


def _add_synonyms(left_content, base_word_, search_synonym):
    """Adds synonyms to database

    Keyword arguments:
    left_content -- the portion of the merriam-webster webpage that stores the
    pertinent information for building our entry
    base_word_ -- BaseWord object associated with the word we are looking up
    search_synonym -- tells us whether to lookup the synonyms or stow them in
    the SynonymsToLookUp table

    Adds synonyms listed on page, checks to see if words are in database,
    if they are not, call scrape_word() to add them and then add to database.

    The large issue with getting synonyms on Merriam-Webster is that sometimes
    Merriam-Webster's entry for a word does not have the synonym/antonym section
    that most entries do. However, there's another section that contains a list
    of synonyms. _scrape_main_synonym_section() handles the default synonym
    section, while _scrape_alternative_synonym_section() handles the alternative
    synonym section. They return a list that contains a tuple that stores a list
    of words to add to the dictionary and synonym table.
    """
    try:
        synonym_list = _scrape_main_synonym_section(left_content)
    except AttributeError:
        try:
            synonym_list = _scrape_alternative_synonym_section(left_content)
        except AttributeError:
            return
    if search_synonym:
        _create_synonyms(left_content, base_word_, synonym_list)
    else:
        _create_synonym_lookups(left_content, base_word_, synonym_list)


def _scrape_main_synonym_section(left_content):
    """Scrapes the main/default synonym section for a word.

    If there is no pos listed, use the one listed for the word
    """
    synonym_header = left_content.find('div',
                                      {'class' : 'synonyms_list'})
    synonym_labels = synonym_header.find_all('p',
                                            {'class' : 'function-label'})
    synonym_lists = synonym_header.find_all('p', {'class' : None})
    if len(synonym_labels) != len(synonym_lists):
        raise ValueError('There are an uneven number of labels and lists')
    synonym_list = []
    for label, s_list in zip(synonym_labels, synonym_lists):
        word_list = s_list.find_all('a')
        word_list_text = [word for word in word_list]
        pos_synonym_flag = label.getText().lower()
        synonym_list.append((pos_synonym_flag, word_list_text))
    return synonym_list


def _scrape_alternative_synonym_section(left_content):
    """Scrapes the alternative synonym listing"""
    synonym_header = left_content.find('div',
                                      {'class' : 'syns_discussion'})
    synonym_lists = synonym_header.find_all('p', {'class' : 'syn'})
    synonym_list = []
    for s_list in synonym_lists:
        word_list = s_list.find_all('a')
        word_list_text = [word for word in word_list]
        #Only will list synonyms, so just add synonym as flag
        synonym_flag = 'synonyms: '
        synonym_list.append((synonym_flag, word_list_text))
    return synonym_list


def _create_synonyms(left_content, base_word_, synonym_list):
    """Creates synonyms for a word"""
    p = re.compile('(^[\w\-]*)')
    for (pos_synonym_flag, word_list) in synonym_list:
        for word in word_list:
            variant_word_set = models.VariantWord.objects.values_list('name',
                                                                      flat=True)
            word_text = _clean_word_name(word.getText().lower())
            if word_text == base_word_.name:
                continue
            m = p.match(pos_synonym_flag)
            synonym_flag = m.group(1)
            if word_text not in variant_word_set:
                synonym_variant_word = _handle_creating_synonyms(word_text,
                                           variant_word_set, synonym_flag)
            else:
                synonym_variant_word = models.VariantWord.objects.all() \
                                             .get(name=word_text)
            if synonym_flag == 'synonyms':
                _, _ = models.Synonym.objects \
                             .get_or_create(base_word=base_word_,
                                            synonym=synonym_variant_word)
            else:
                _, _ = models.Antonym.objects \
                             .get_or_create(base_word=base_word_,
                                            antonym=synonym_variant_word)


def _create_synonym_lookups(left_content, base_word_, synonym_list):
    """Stows away synonyms to lookup when we don't have to look them up now"""
    p = re.compile('(^[\w\-]*)')
    for (pos_synonym_flag, word_list) in synonym_list:
        for word in word_list:
            word_text = _clean_word_name(word.getText().lower())
            if word_text == base_word_.name:
                continue
            m = p.match(pos_synonym_flag)
            synonym_flag = m.group(1)
            is_synonym = synonym_flag == 'synonyms'
            _, _ = models.SynonymsToLookUp.objects \
                         .get_or_create(base_word=base_word_,
                                        lookup_word=word_text,
                                        is_synonym=is_synonym)


def _handle_creating_synonyms(word_text, variant_word_set, synonym_flag):
    """Adds synonym to db and returns the associated base word

    Keyword arguments:
    word_text -- the synonym/anonym listed to lookup
    variant_word_set -- list of all different spellings of words in the db

    Sometimes a word will be listed as a synonym that and has an entry page that
    lists an alternative spelling that has its own page. If later on, a synonym
    for a different word lists an alternative spelling of the word with its own
    page, this can cause a failure to lookup a word successfully. For example,
    if we look up the word 'capricious,' it lists 'settled' as an antonym.
    'Settled' directs to the 'settle' entry that lists 'settling' as an
    alternative form of the word. The word 'precipitate' lists 'settlings' as a
    synonym. 'settlings' does not show up as an alternative form/spelling for
    'settle.' Thus, we would look up 'settlings,' which goes to the 'settling'
    page. When we try to add 'settling' to the database, there will be an error,
    because 'settling' was already added to the variant word set. Thus, we try
    to remove an 's' if the main spelling fails.
    """
    if synonym_flag == 'synonyms':
        msg = 'synonym'
    else:
        msg = 'antonym'
    print(f'looking up the {msg}: {word_text}')
    time.sleep(2)
    try:
        scrape_word(word_text)
    except IntegrityError:
        word_text = re.sub('s$', '', word_text)
        if word_text not in variant_word_set:
            scrape_word(word_text)
    return models.VariantWord.objects.all().get(name=word_text)


def _load_word_list(filename):
    """Reads file of words into list"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f]
