from os import environ
from typing import Dict

import pymongo
import json
from tqdm import tqdm

from importlib import import_module

prepare_data = import_module('01_prepare_data')

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
   
    all_unlabeled_papyri = list(collection.find({ 'grammateus_type': {'$exists': 0}, 'block_index': 1}, 
                                                {'training_text': 1, 'text_classes': 1, 'hgv_title': 1, 'id': 1, 'tm_id':1, 'block_index': 1, '_id':0}))

    all_unlabeled_papyri = prepare_data.combine_blocks(all_unlabeled_papyri)


    all_papyri_preprocessed = [preprocess(papyrus) for papyrus in all_unlabeled_papyri]

    with open('all_unlabeled.json', 'w') as f:
        json.dump(all_papyri_preprocessed, f)

def preprocess(papyrus):
    preprocessed = prepare_data.preprocess(papyrus['training_text']) 

    return {'text': preprocessed, 'meta': papyrus}


if __name__=="__main__":
    main()
