from os import environ
from typing import Dict

import pymongo
import json
from tqdm import tqdm

import spacy
spacy.prefer_gpu()
from spacy.lang.de.stop_words import STOP_WORDS

from importlib import import_module

prepare_data = import_module('01_prepare_data')

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
   
    all_unlabeled_papyri = list(collection.find({'text_classes' : {'$exists': 1}, 'grammateus_type': {'$exists': 0}}, 
        {'training_text': 1, 'text_classes': 1, 'hgv_title': 1, 'id': 1, 'tm_id':1,'_id':0}))


    nlp_blank = spacy.blank('de')
    all_papyri_preprocessed = [preprocess(papyrus, nlp_blank) for papyrus in all_unlabeled_papyri]
     
    classifier = spacy.load('model/model-best')

    all_papyri_processed = []


    text_classes, papyri = zip(*all_papyri_preprocessed)


    all_cats = []
    for doc in tqdm(classifier.pipe(text_classes)):
        cat = get_cat(doc.cats)

        all_cats.append(cat)

    all_papyri_processed = [{'grammateus_type': grammateus_type, **papyrus} for grammateus_type, papyrus in zip(all_cats, papyri)]

    print(all_papyri_processed[:10])
    
    with open('papyri_with_classes.json', 'w') as f:
        json.dump(all_papyri_processed, f)
        
def get_cat(cats: Dict[str, float]):
    max_score = 0
    max_cat = None
    for cat, score in cats.items():
        if score > max_score:
            max_score = score
            max_cat = cat
    
    return max_cat

def preprocess(papyrus, nlp):
    text_classes = prepare_data.preprocess(papyrus['text_classes'], papyrus['hgv_title'], nlp)

    return (text_classes, papyrus)


if __name__=="__main__":
    main()
