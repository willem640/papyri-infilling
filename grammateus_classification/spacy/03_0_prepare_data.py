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
                                                {'training_text': 1, 'text_classes': 1, 'hgv_title': 1, 'id': 1, 'tm_id':1,'block_index' : 1,'file_id': 1, '_id':0}))

    first_blocks = [block for block in all_unlabeled_papyri if block['block_index'] == 1]
    other_blocks = [block for block in all_unlabeled_papyri if block['block_index'] != 1]


    nlp_blank = spacy.blank('grc')
    first_blocks_preprocessed = [preprocess(papyrus, nlp_blank) for papyrus in first_blocks]
     
    classifier_input, _ = zip(*first_blocks_preprocessed)

    with open('03_classifier_input.json', 'w') as f:
        json.dump(classifier_input, f)

    with open('03_first_blocks.json', 'w') as f:
        json.dump(first_blocks, f)
    
    with open('03_other_blocks.json', 'w') as f:
        json.dump(other_blocks, f)


def preprocess(papyrus, nlp):
    classifier_input = prepare_data.preprocess(papyrus['text_classes'], papyrus['hgv_title'], papyrus['training_text'], nlp)

    return (classifier_input, papyrus)


if __name__=="__main__":
    main()
