from django.db import models


class BaseWord(models.Model):
    """Contains base form or plain form of a word.

    Variants such as plurals or different tenses are stored in the VariantWord
    class. Links to different definitions.
    """
    name = models.CharField(max_length=50, unique=True)

    def return_pos_list(self):
        """Returns the list of parts of speech associated for a word"""
        form_words = self.formword_set
        return [form_word.pos.name for form_word in form_words.all()]

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'BaseWord({self.id!r}, {self.name!r})'


class PartOfSpeech(models.Model):
    """Part of speech of a word"""
    name = models.CharField(max_length=15, unique=True)
    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'PartOfSpeech({self.id!r}, {self.name!r})'


class FormWord(models.Model):
    """Unique stores the list of parts of speech for each base word"""
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    pos = models.ForeignKey(PartOfSpeech, on_delete=models.CASCADE)
    unique_together = ('base_word', 'pos')

    def __str__(self):
        return f'word: {self.base_word.name}, pos: {self.pos}'

    def __repr__(self):
        return f'FormWord({self.id!r}, {self.base_word!r}, {self.pos!r})'


class VariantWord(models.Model):
    """Contains all different forms of a word. Plurals, past tense, etc.

    Many to one relationship with BaseWord.
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
    """An example of a word used in a sentence for a definition of a word."""
    definition = models.ForeignKey(WordDefinition, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.definition}\nsentence: {self.sentence}'

    def __repr__(self):
        return (f'ExampleSentence({self.id!r}, {self.definition!r},'
                f'{self.sentence!r})')


class Synonym(models.Model):
    """Word that has a similar meaning to a FormWord.

    Need to validate that base_word is not equal to the synonym. Unsure if I
    can do this within the model method or if this validation should just be
    handled when creating the database.
    """
    form_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    synonym = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    unique_together = ('form_word', 'synonym')

    def __str__(self):
        return f'{self.form_word} Synonym: {self.synonym}'

    def __repr__(self):
        return f'Synonym({self.id!r}, {self.form_word!r}, {self.synonym!r})'


class Antonym(models.Model):
    """Word that has the oppositing meaning to a base word.

    Same issue of validating as commented in the synonym class
    """
    form_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    antonym = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    unique_together = ('form_word', 'antonym')

    def __str__(self):
        return f'{self.form_word} Antonym: {self.antonym}'

    def __repr__(self):
        return f'Antonym({self.id!r}, {self.form_word!r}, {self.antonym!r})'
