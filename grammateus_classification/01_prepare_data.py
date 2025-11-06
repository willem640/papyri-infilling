from os import environ
import random
import string

import pymongo
from spacy.lang.de.stop_words import STOP_WORDS
import spacy
from spacy.language import Language
from spacy.tokens import DocBin
from tqdm import tqdm

# TODO reproducible test/dev/train sets, plus ensure correct distribution in test/dev/train?

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    

    types_and_classes = []
    for papyrus in collection.find({'grammateus_type': {'$exists': True}, 'text_classes': {'$exists' : True}}, {'text_classes': 1, 'grammateus_type': 1, '_id': 0}):
       types_and_classes.append((papyrus['text_classes'], papyrus['grammateus_type']))

    nlp = spacy.blank("de")

    types_and_classes_preprocessed = [(preprocess(terms), grammateus_type)  
                for terms, grammateus_type in types_and_classes]
   

    random.Random(42).shuffle(types_and_classes_preprocessed)

    split_idx_test = int(len(types_and_classes_preprocessed) * 0.1)
    split_idx_dev = int(len(types_and_classes_preprocessed) * 0.2)
    train_data = types_and_classes_preprocessed[split_idx_dev:]
    dev_data = types_and_classes_preprocessed[split_idx_test:split_idx_dev]
    test_data = types_and_classes_preprocessed[:split_idx_test]


    print(f"Total: {len(types_and_classes_preprocessed)} - Train:  {len(train_data)} - Dev: {len(dev_data)} - Test: {len(test_data)}")
    write_to_disk(train_data, "train.spacy", nlp)
    write_to_disk(dev_data, "dev.spacy", nlp)
    write_to_disk(test_data, "test.spacy", nlp)

def write_to_disk(data, filename, nlp: Language):
    db = DocBin()

    types = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]
    for doc, label in nlp.pipe(data, as_tuples=True):
        for grammateus_type in types:
            doc.cats[grammateus_type] = label == grammateus_type
        db.add(doc)
    db.to_disk(filename)

def preprocess(terms):
  

    return " ".join(terms)

if __name__=="__main__":
	main()
