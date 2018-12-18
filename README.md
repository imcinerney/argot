## argot
argot tries to solve the problem of looking up a word and forgetting it 20 minutes later, by having your dictionary keep track of words you searched. Users can create lists for different works they are reading or just keep one for all the words they are unfamiliar with. argot works by scraping a word's definition, synonyms, parts of speech, different spellings, etc., and uses Django to store and organize this information. Users can create word lists to keep track of words that they look up and use argot to quiz themselves on their meaning.

## Motivation
While reading Infinite Jest, I was constantly opening my dictionary to look up some obscure, esoteric word. This word would often be one that I would want to remember, but due to the volume of other words I was looking up, I probably only retained the meaning of the word 10% of the time. Thus, I wanted to create a website that would allow you to look up a word and keep track of what words you looked up so you can:
  A) remember what words you looked up and B) quiz yourself on these words' meanings.

## Build status
Currently working towards something resembling an alpha build. The website itself is quite ugly, but will devote time to improve this once most of the functionality has been built.

## Tech/framework used
<b>Built with</b>
- [Django](https://www.djangoproject.com/)

## Installation
argot uses [python3](https://www.python.org/downloads/) to run. After you download python3, you'll need to create a virtual environment and install the required packages.
Here are instructions on how to setup a virtual environment on the major operating systems. Run the following commands in the root directory of the repository:

Mac OS/Linux
--------------
```
python3 -m venv env
source env/bin/activate  
pip install -r requirements.txt  
```

Windows
--------------
```
python -m virtualenv env  
.\env\Scripts\activate  
pip install -r requirements.txt  
```

Currently, there is no database stored/tracked in this repository. To create one, type ```python manage.py migrate``` (or ```python3 manage.py migrate``` if you have Mac). This creates all the tables used to store and process the data for the website. It also loads the database with an initial set of data of 53 words.  

To visit the website, type ```python manage.py runserver``` and then type in http://127.0.0.1:8000 in your browser to see the website. Initially, when you look up words, it will be quite slow, because the database does not have any entries. However, once you look up a word, you won't need to again.  

To further fill the database with more entries, type in the following commands:  
```
python manage.py shell
>>> from dictionary import merriam_webster_scraper as mws
>>> mws.fill_in_synonyms()
```
This will lookup and add all synonyms and antonyms listed for each word in the database whose synonyms/antonyms we haven't looked up already. In the initial data, none of the synonyms or antonyms have been created for any of the words, so this will look up all of the synonyms and antonyms of the words in the database.  

## Tests
All tests reside in the dictionay/test.py file. To run them, type ```python manage.py test``` into the root directory.

## Contribute
If you want to contribute, feel free to open issues or pull requests. Or if you want to talk about the project, the Celtics, or Infinite Jest, feel free to email me at ian.g.mcinerney@gmail.com.
