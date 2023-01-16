import re
import nltk
import pandas as pd
import numpy as np
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import spacy
from country_list import countries_for_language
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
countries_De = dict(countries_for_language('de')).values()
countries_En = dict(countries_for_language('en')).values()

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')



bert_tokenizer = AutoTokenizer.from_pretrained('dslim/bert-large-NER')
bert_model = AutoModelForTokenClassification.from_pretrained('dslim/bert-large-NER')

english_nlp = spacy.load('en_core_web_sm')
german_nlp = spacy.load('de_core_news_sm')
csv = pd.read_csv("German-Zip-Codes.csv", delimiter=";", dtype = {'Plz': str, 'Vorwahl': str})

class PrivacyFilter:

    def identify_birthdays(self, text, timestamp_format):
        patterns = []
        #dd/mm/yyyy (with .-/)
        patterns.append(r"(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[012])[-/.](?:19\d{2}|20[012][0-9])\b")
        #dd/mm/yy (with .-/)
        patterns.append(r"(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[012])[-/.]\d{2}\b")
        #yyyy/mm/dd
        patterns.append(r"(?:19\d{2}|20[012][0-9]|2020)[-/.](?:0?[1-9]|1[012])[-/.](?:0?[1-9]|[12][0-9]|3[01])\b")
        #yy/mm/dd
        patterns.append(r"\d{2}[-/.](?:0?[1-9]|1[012])[-/.](?:0?[1-9]|[12][0-9]|3[01])\b")
        #mm/dd/yyyy
        patterns.append(r"(?:0?[1-9]|1[012])[-/.](?:0?[1-9]|[12][0-9]|3[01])[-/.](?:19\d{2}|20[012][0-9])\b")
        #mm/dd/yy
        patterns.append(r"(?:0?[1-9]|1[012])[-/.](?:0?[1-9]|[12][0-9]|3[01])[-/.]\d{2}\b")
        results = []
        for pattern in patterns:
            results.extend(re.findall(pattern, text))
        if len(results) > 0:
            return "Found birthday in text"

    def identify_email(self, text):
        pattern = r"(?:|\s)[\w!#$%&'*+/=?^`{|}~\"-](\.?[\w!#$%&'*+/=?^`{|}~-]+)*(\".*\")*@\w+[.-]?\w*\.[a-zA-Z]{2,6}\b"
        results = re.findall(pattern, text)
        if len(results) > 0:
            return "Found email in text"

    def identify_postal_codes(self, text):
        results = []
        patterns = csv.Plz.values
        for pattern in patterns:
            pattern = r"\b" + pattern + r"\b"
            results.extend(re.findall(str(pattern), text))
        if len(results) > 0:
            return "Found german ZIP code in text"

    
    def identify_names(self, text):
        """
        #recall/precision english model: 0.84
        spacy_parser = english_nlp(text)
        for entity in spacy_parser.ents:
            if entity.label_ in ["PER", "PERSON"]:
                return "Found name"
        #recall/precision german model: 0.83/ 0.82
        spacy_parser = german_nlp(text)
        for entity in spacy_parser.ents:
            if entity.label_ in ["PER", "PERSON"]:
                return "Found name"
        """
        nlp = pipeline('ner', model=bert_model, tokenizer=bert_tokenizer)
        res = nlp(text)
        res = [e["entity"] for e in res]
        res = [e for e in res if "PER" in e]
        if len(res) > 0:
            return True


    def identify_nationality(self, text):
        if len(re.findall(r"({})".format("|".join(countries_De)), text)) > 0:
            return "Found german country"
        if len(re.findall(r"({})".format("|".join(countries_En)), text)) > 0:
            return "Found english country"

    def filter(self, text):
        results = []
        results.append(self.identify_birthdays(text, None))
        results.append(self.identify_email(text))
        results.append(self.identify_postal_codes(text))
        results.append(self.identify_nationality(text))
        results.append(self.identify_names(text))
        return results


"""
filter = PrivacyFilter()
text = '''
This is a sample text that contains the name Alex Smith who is one of the developers of this project.
You can also find the surname Jones here and this means Corbinian lives in Schrobenhausen or Aalen or Buxdehude. Meine Adresse ist: Am schönen See 13. Ein Werkzeug ist meine Pipeline. Das sind keine Namen.
My log-data is bliblablubb. Das sind Nationalitäten: Deutschland, England, Großbritannien, Japan. These are nationalities: America, Brazil, Portugal. Meine Nationalität ist deutsch.
25/09/1994 und 1994/02/03 oder 19.2.93 2022-01-02. Meine Lieblings-ZIP-Codes sind 97616, 81371 und 85049. c.nentwich@gmx.de , ga67xer@mytum.de 123@456.xr
'''
print(filter.filter(text))
"""
