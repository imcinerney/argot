from django.test import TestCase

from .models import BaseWord, FormWord, PartOfSpeech, WordDefinition
from dictionary import merriam_webster_scraper as mws
from bs4 import BeautifulSoup
import os


class BaseWordModelTest(TestCase):
    def setUp(self):
        back = BaseWord.objects.create(name='back')
        noun = PartOfSpeech.objects.create(name='noun')
        verb = PartOfSpeech.objects.create(name='verb')
        abverb = PartOfSpeech.objects.create(name='abverb')
        adjective = PartOfSpeech.objects.create(name='adjective')
        form1 = FormWord.objects.create(base_word=back, pos=noun)
        form2 = FormWord.objects.create(base_word=back, pos=verb)
        form3 = FormWord.objects.create(base_word=back, pos=abverb)
        form4 = FormWord.objects.create(base_word=back, pos=adjective)

    def test_pos_list(self):
        """Make sure the return_pos_list() function works correctly"""
        back = BaseWord.objects.get(name='back')
        self.assertEqual(back.return_pos_list(), ['noun', 'verb', 'abverb',
                                                  'adjective'])


class ScraperHelperFunctionTest(TestCase):
    """Class to test all of the non-web functions"""
    def test_clean_pos_text(self):
        """Test a number of cases of the clean pos text function"""
        self.assertEqual(mws._clean_pos_text('noun21-30asdf'), 'noun')
        self.assertEqual(mws._clean_pos_text('verb:'), 'verb')
        self.assertEqual(mws._clean_pos_text('abverb-sense1:'), 'abverb')


class BackDefinitionEntryTest(TestCase):
    """Class to test that the scraper successfully extracts info from the
    entry of the word 'back'"""
    def setUp(self):
        back_html = os.path.join('dictionary', 'html_test_pages', 'back.html')
        soup = BeautifulSoup(open(back_html), 'html5lib')
        mws._manage_dictionary_entries(soup, 'back', False)

    def test_db_created_successfully(self):
        base_words = BaseWord.objects.all()
        self.assertEqual(list(base_words.values_list('name', flat=True)),
                         ['back'])
        db_pos_list = base_words[0].return_pos_list()
        pos_list = ['noun',
                    'adverb',
                    'adjective',
                    'verb',
                    'geographical name',
                   ]
        self.assertEqual(db_pos_list, pos_list)
        db_definitions = list(WordDefinition.objects.all()
                                            .values_list('definition',
                                                          flat=True))
        definitions = ['the rear part of the human body especially from the'
                           ' neck to the end of the spine',
                       'the body considered as the wearer of clothes',
                       'capacity for labor, effort, or endurance',
                       "the back considered as the seat of one's awareness of"
                           " duty or failings",
                       "the back considered as an area of vulnerability",
                       "the part of a lower animal (such as a quadruped) "
                           "corresponding to the human back",
                       "spinal column",
                       "spine",
                       "the side or surface opposite the front or face",
                       "the rear part",
                       "the farther or reverse side",
                       "something at or on the back for support",
                       "a place away from the front",
                       "a position in some games (such as football or soccer) "
                           "behind the front line of players",
                       "a player in this position",
                       "a swimming race in which swimmers use the backstroke",
                       "to, toward, or at the rear",
                       "in or into the past",
                       "backward in time",
                       "ago",
                       "to or at an angle off the vertical",
                       "under restraint",
                       "in a delayed or retarded condition",
                       "in an inferior or secondary position",
                       "behind a competitor in points or ranking",
                       "to, toward, or in a place from which a person or thing "
                            "came",
                       "to or toward a former state",
                       "in return or reply",
                       "being at or in the back",
                       "distant from a central or main area",
                       "articulated at or toward the back of the oral passage",
                       "formed deep within the mouth",
                       "having returned or been returned",
                       "being in arrears",
                       "overdue",
                       "moving or operating backward",
                       "reverse",
                       "not current",
                       "constituting the final 9 holes of an 18-hole course",
                       "to support by material or moral assistance",
                       "substantiate",
                       "to assume financial responsibility for",
                       "to provide musical accompaniment for",
                       "to cause to go back or in reverse",
                       "to articulate (a speech sound) with the tongue farther"
                            " back",
                       "to form deeper within the mouth",
                       "to furnish with a rear part",
                       "to furnish with a back",
                       "to be at the rear part of",
                       "to be at the back of",
                       "to move backward",
                       "to shift counterclockwise",
                       "to have the rear part facing in the direction of "
                            "something",
                       "river 605 miles (974 kilometers) long in Nunavut, "
                            "Canada, rising along the border with the Northwest"
                            " Territories and flowing east-northeast into the "
                            "Arctic Ocean",
                       ]
        self.assertEqual(db_definitions, definitions)


class BolsterDefinitionEntryTest(TestCase):
    """Class to test that the scraper successfully extracts info from the
    entry of the word 'bolster'"""
    def setUp(self):
        bolster_html = os.path.join('dictionary', 'html_test_pages',
                                    'bolster.html')
        soup = BeautifulSoup(open(bolster_html, encoding='utf-8'), 'html5lib')
        mws._manage_dictionary_entries(soup, 'bolster', False)

    def test_db_created_successfully(self):
        base_words = BaseWord.objects.all()
        self.assertEqual(list(base_words.values_list('name', flat=True)),
                         ['bolster'])
        db_pos_list = base_words[0].return_pos_list()
        pos_list = ['noun',
                    'verb',
                   ]
        self.assertEqual(db_pos_list, pos_list)
        db_definitions = list(WordDefinition.objects.all()
                                            .values_list('definition',
                                                          flat=True))
        definitions = [
                        'a long pillow or cushion',
                        'a structural part designed to eliminate friction or '
                            'provide support or bearing',
                        'to support with or as if with a bolster',
                        'reinforce',
                        'to give a boost to',
                       ]
        self.assertEqual(db_definitions, definitions)


class CapriciousPrecipitateDefinitionEntryTest(TestCase):
    """Class to test that the scraper successfully extracts info from the
    entry of the word 'capricious' and then 'precipitate'"""
    def setUp(self):
        precipitate_html = os.path.join('dictionary', 'html_test_pages',
                                        'precipitate.html')
        soup = BeautifulSoup(open(precipitate_html, encoding='utf-8'),
                             'html5lib')
        mws._manage_dictionary_entries(soup, 'precipitate', False)
        capricious_html = os.path.join('dictionary', 'html_test_pages',
                                       'capricious.html')
        soup = BeautifulSoup(open(capricious_html, encoding='utf-8'),
                                  'html5lib')
        mws._manage_dictionary_entries(soup, 'capricious', False)


    def test_db_created_successfully(self):
        db_base_words = BaseWord.objects.all()
        base_word_list = ['precipitate', 'capricious']
        self.assertEqual(list(db_base_words.order_by('id')
                                           .values_list('name', flat=True)),
                         base_word_list)
        db_pos_list = db_base_words[0].return_pos_list()
        pos_list = [
                    'verb',
                    'noun',
                    'adjective',
                   ]
        db_pos_list = db_base_words[1].return_pos_list()
        pos_list = ['adjective']
        self.assertEqual(db_pos_list, pos_list)
        db_definitions = list(WordDefinition.objects.all()
                                            .values_list('definition',
                                                          flat=True))
        definitions = [
                        'to throw violently',
                        'hurl',
                        'to throw down',
                        'to bring about especially abruptly',
                        'to cause to separate from solution or suspension',
                        'to cause (vapor) to condense and fall or deposit',
                        'to fall headlong',
                        'to fall or come suddenly into some condition',
                        'to move or act with violent or unwise speed',
                        'to separate from solution or suspension',
                        'to condense from a vapor and fall as rain or snow',
                        'a substance separated from a solution or suspension by'
                            ' chemical or physical change usually as an '
                            'insoluble amorphous or crystalline solid',
                        'a product, result, or outcome of some process or '
                            'action',
                        'falling, flowing, or rushing with steep descent',
                        'precipitous, steep',
                        'exhibiting violent or unwise speed',
                        'governed or characterized by caprice',
                        'impulsive, unpredictable',
                       ]
        self.assertEqual(db_definitions, definitions)
