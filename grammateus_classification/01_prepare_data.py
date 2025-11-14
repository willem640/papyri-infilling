from os import environ
import random
import string
import re

import pymongo
from spacy.lang.en.stop_words import STOP_WORDS
import spacy
from spacy.language import Language
from spacy.tokens import DocBin
from tqdm import tqdm
from libretranslatepy import LibreTranslateAPI

# TODO reproducible test/dev/train sets, plus ensure correct distribution in test/dev/train?

GRAMMATEUS_TYPES = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    

    types_and_classes = []
    for papyrus in collection.find({'grammateus_type': {'$exists': True}, 'text_classes': {'$exists' : True}}, {'text_classes': 1, 'grammateus_type': 1, 'hgv_title': 1, '_id': 0}):
       types_and_classes.append((papyrus['text_classes'], papyrus['hgv_title'], papyrus['grammateus_type']))

    nlp = spacy.blank("en")

    types_and_classes_preprocessed = [(preprocess(terms, title, nlp), grammateus_type)  
                for terms, title, grammateus_type in tqdm(types_and_classes)]
   
    train_data = []
    dev_data = []
    test_data = []


    # ensure equal distribution in train, dev and test sets
    for grammateus_type in GRAMMATEUS_TYPES:
        types_and_classes_single_type = [type_and_classes for type_and_classes in types_and_classes_preprocessed if type_and_classes[1] == grammateus_type]
        train, dev, test = test_dev_train_split(types_and_classes_single_type)
        train_data.extend(train)
        dev_data.extend(dev)
        test_data.extend(test)


    print(f"Total: {len(types_and_classes_preprocessed)} - Train:  {len(train_data)} - Dev: {len(dev_data)} - Test: {len(test_data)}")
    write_to_disk(train_data, "train.spacy", nlp)
    write_to_disk(dev_data, "dev.spacy", nlp)
    write_to_disk(test_data, "test.spacy", nlp)


def test_dev_train_split(data_list, random_seed=42):

    random.Random(random_seed).shuffle(data_list)

    split_idx_test = int(len(data_list) * 0.1)
    split_idx_dev = int(len(data_list) * 0.2)
    train_data = data_list[split_idx_dev:]
    dev_data = data_list[split_idx_test:split_idx_dev]
    test_data = data_list[:split_idx_test]

    return train_data, dev_data, test_data

def write_to_disk(data, filename, nlp: Language):
    db = DocBin()

    for doc, label in nlp.pipe(data, as_tuples=True):
        for grammateus_type in GRAMMATEUS_TYPES:
            doc.cats[grammateus_type] = label == grammateus_type
        db.add(doc)
    db.to_disk(filename)

def preprocess(terms, title, nlp: Language):
    joined_terms_translated = " ".join([translate(term, source_lang="de") for term in terms])
    title_translated = translate(title) if title != 'keiner' else ''
    preprocessed_title = remove_punctuation_stopwords(title_translated, nlp)
    preprocessed_terms = remove_punctuation_stopwords(joined_terms_translated, nlp)
    if (len(preprocessed_title) < 3 or len(preprocessed_terms) < 3) and title != 'keiner':
        print(f"Terms/Title too short. Title: {title}\tterms: {terms}")
    return f"{preprocessed_title} {preprocessed_terms}"

def remove_punctuation_stopwords(text, nlp: Language):
    tokens = [token.text for token in nlp(text)]
    tokens = [token for token in tokens if
              token not in STOP_WORDS and
              token not in string.punctuation and
              len(token) > 3]

    return " ".join(tokens)

def detect_lang(text,
                possible_langs,
                api: LibreTranslateAPI,
                try_backup_options=True):

    detected_langs = api.detect(text)

    possible_langs = list(filter(lambda lang: lang['language'] in possible_langs, detected_langs))
    
    if len(possible_langs) == 0:
        text_lang = None
        if try_backup_options:
            text_split = text.strip().split(" ")
            text_lang = detect_lang(text_split[0], possible_langs, api, try_backup_options=False)

            if text_lang is None:
                exceptions = {
                        r"[bB]rief": "de",
                        r"[qQ]uittung": "de",
                        r"Bankakt": "de",
                        r"[aA]kten": "de",
                        r"[lL]iste": "de",
                        r"[dD]eklaration": "de",
                        r"[rR]equête": "fr",
                        r"[aA]rgent": "fr",
                        r"Ricevuta": "it",
                }
                for pattern, language in exceptions.items():
                    if re.search(pattern, text):
                        text_lang = language
                        break

        if text_lang is None:
            return None
        else:
            # A backup option worked!
            return text_lang

    text_lang = max(possible_langs, key=lambda lang: lang['confidence'])['language'] 

    return text_lang

def translate(text,
              source_lang=None,
              target_lang="en",
              possible_langs=["en", "de", "fr", "it"],
              api: LibreTranslateAPI = LibreTranslateAPI("http://127.0.0.1:5000")):
    if source_lang is None:
        if (text_lang := detect_lang(text, possible_langs, api)) is None:
            print(f"Could not find language for \"{text}\", using as-is.")
            return text
    else:
        text_lang = source_lang
    
    if text_lang == target_lang:
        return text

    return api.translate(text, text_lang, target_lang)




def preprocess_terms(terms, nlp: Language):
    text = " ".join(terms)
    tokens = remove_punctuation_stopwords(text, nlp)
    return " ".join(tokens)

if __name__=="__main__":
	main()
