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


class PartOfSpeech(models.Model):
    """Part of speech of a word"""
    name = models.CharField(max_length=15, unique=True)


class FormWord(models.Model):
    """Unique stores the list of parts of speech for each base word"""
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    pos = models.ForeignKey(PartOfSpeech, on_delete=models.CASCADE)
    unique_together = ('base_word', 'pos')


class VariantWord(models.Model):
    """Contains all different forms of a word. Plurals, past tense, etc.

    Many to one relationship with BaseWord.
    """
    base_word = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)


class WordDefinition(models.Model):
    """Contains all the listed definitions for a word."""
    form_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    definition = models.CharField(max_length=300)


class ExampleSentence(models.Model):
    """An example of a word used in a sentence for a definition of a word."""
    definition = models.ForeignKey(WordDefinition, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=300)


class Synonym(models.Model):
    """Word that has a similar meaning to a FormWord.

    Need to validate that base_word is not equal to the synonym. Unsure if I
    can do this within the model method or if this validation should just be
    handled when creating the database.
    """
    base_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    synonym = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    unique_together = ('base_word', 'synonym')


class Antonym(models.Model):
    """Word that has the oppositing meaning to a base word.

    Same issue of validating as commented in the synonym class
    """
    base_word = models.ForeignKey(FormWord, on_delete=models.CASCADE)
    antonym = models.ForeignKey(BaseWord, on_delete=models.CASCADE)
    unique_together = ('base_word', 'synonym')
