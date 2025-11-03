from os import environ
import random
import string

import pymongo
from spacy.lang.de.stop_words import STOP_WORDS
import spacy
from spacy.language import Language
from spacy.tokens import DocBin
from tqdm import tqdm

def main():
    grammateus_path = environ.get("GRAMMATEUS_CSV", "grammateus.csv")
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    

    types_and_classes = []
    for papyrus in collection.find({'grammateus_type': {'$exists': True}, 'text_classes': {'$exists' : True}}, {'text_classes': 1, 'grammateus_type': 1, '_id': 0}):
       types_and_classes.append((papyrus['text_classes'], papyrus['grammateus_type']))

    nlp = spacy.blank("de")

    types_and_classes_preprocessed = [(preprocess(terms, nlp), grammateus_type)  
                for terms, grammateus_type in types_and_classes]
   

    random.shuffle(types_and_classes_preprocessed)

    split_idx = int(len(types_and_classes_preprocessed) * 0.1)
    train_data = types_and_classes_preprocessed[split_idx:]
    test_data = types_and_classes_preprocessed[:split_idx]


    print(f"Total: {len(types_and_classes_preprocessed)} - Train:  {len(train_data)} - Test: {len(test_data)}")
    write_to_disk(train_data, "train_concat.spacy", nlp)
    write_to_disk(test_data, "test_concat.spacy", nlp)

def write_to_disk(data, filename, nlp: Language):
    db = DocBin()
    docs = []
    

    types = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]
    for doc, label in nlp.pipe(data, as_tuples=True):
        for grammateus_type in types:
            doc.cats[grammateus_type] = label == grammateus_type
        db.add(doc)
    db.to_disk(filename)

def preprocess(terms, nlp: Language):
    text = " ".join(terms)
    tokens = [token.text for token in nlp(text)]
    
    tokens = [token for token in tokens if
              token not in STOP_WORDS and
              token not in string.punctuation and
              len(token) > 3]

    return " ".join(tokens)

if __name__=="__main__":
	main()
