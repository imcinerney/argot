from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F


class BaseWord(models.Model):
    """Contains base form or plain form of a word.

    Variants such as plurals or different tenses are stored in the VariantWord
    class. Unique record for each dictionary entry
    """
    name = models.CharField(max_length=50, unique=True)
    searched_synonym = models.BooleanField(default=False)

    def return_pos_list(self):
        """Returns the list of parts of speech associated for a word"""
        form_words = self.formword_set
        return [form_word.pos.name for form_word in form_words.all()]

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return (f'BaseWord({self.id!r}, {self.name!r}, '
                f'{self.searched_synonym!r})')


class PartOfSpeech(models.Model):
    """Part of speech of a word"""
    name = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'PartOfSpeech({self.id!r}, {self.name!r})'


class FormWord(models.Model):
    """Stores the list of parts of speech for each base word"""
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    pos = models.ForeignKey(PartOfSpeech, on_delete=models.CASCADE)
    unique_together = ('base_word', 'pos')

    def __str__(self):
        return f'word: {self.base_word.name}, pos: {self.pos}'

    def __repr__(self):
        return f'FormWord({self.id!r}, {self.base_word!r}, {self.pos!r})'


class VariantWord(models.Model):
    """Contains all different forms of a word. Plurals, past tense, etc.

    Used for looking up if a word is in our databse. The VariantWord table
    will contain different spellings so if a user enters a different spelling
    we don't incorrectly say we don't have it.
    """
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'base word: {self.base_word}, alternate_form: {self.name}'

    def __repr__(self):
        return f'VariantWord({self.id!r}, {self.base_word!r}, {self.name!r})'


class WordDefinition(models.Model):
    """Contains all the listed definitions for a word."""
    form_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    definition = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.form_word}\ndefintion: {self.definition}'

    def __repr__(self):
        return (f'WordDefinition({self.id!r}, {self.form_word!r},'
               f' {self.definition!r})')


class ExampleSentence(models.Model):
    """An example of using a word in a sentence for a particular definition."""
    definition = models.ForeignKey(WordDefinition, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.definition}\nsentence: {self.sentence}'

    def __repr__(self):
        return (f'ExampleSentence({self.id!r}, {self.definition!r},'
                f'{self.sentence!r})')


class Synonym(models.Model):
    """Word that has a similar meaning to a FormWord."""
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    synonym = models.ForeignKey(VariantWord, on_delete=models.CASCADE)
    unique_together = ('base_word', 'synonym')

    def __str__(self):
        return f'{self.base_word} Synonym: {self.synonym}'

    def __repr__(self):
        return f'Synonym({self.id!r}, {self.base_word!r}, {self.synonym!r})'


class Antonym(models.Model):
    """Word that has the oppositing meaning to a base word."""
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    antonym = models.ForeignKey(VariantWord, on_delete=models.CASCADE)
    unique_together = ('base_word', 'antonym')

    def __str__(self):
        return f'{self.base_word} Antonym: {self.antonym}'

    def __repr__(self):
        return f'Antonym({self.id!r}, {self.base_word!r}, {self.antonym!r})'


class WordList(models.Model):
    """Contains the name of the list and the user who created the list"""
    list_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)

    @property
    def word_list_length(self):
        list_of_words = self.wordlistentry_set.all()
        return len(list_of_words)

    def __str__(self):
        return f'{self.list_name}'

    def add_word(self, word):
        """Creates an WordListEntry"""
        entry = WordListEntry(word_list=self, word=word)
        entry.save()

    def entries_list(self):
        entries = self.wordlistentry_set.all()
        return [entry.word for entry in entries]


class WordListEntry(models.Model):
    """Stores a record of a word in a word list"""
    word_list = models.ForeignKey(WordList, on_delete=models.CASCADE)
    word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    unique_together = ('word_list', 'word')

    def __str__(self):
        return f'Word List: {self.word_list.list_name}, Word Name: {self.word}'


class Profile(models.Model):
    """Extension of Django-default User, allows us to track active wordlists"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_word_list = models.OneToOneField(WordList, null=True,
                                            on_delete=models.SET_NULL)

    def __str__(self):
        return (f'Username: {self.user.username}, '
                f'active_word_list: {self.active_word_list}')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """We want to create a Profile everytime we create a User"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """We want to save a Pofile everytime we save a User"""
    instance.profile.save()
