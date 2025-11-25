from os import environ
import random
import json
import re

import pymongo
from tqdm import tqdm

#import helper_scripts.llama_util as llama_util


GRAMMATEUS_TYPES = ["Epistolary Exchange", "Transmission of Information", "Objective Statement", "Recording of Information"]

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    

    types_and_classes = list(collection.find(
        {'grammateus_type': {'$exists': True}, 'text_classes': {'$exists': True}},
        {'text_classes': 1, 'grammateus_type': 1, 'hgv_title': 1, 'training_text': 1, 'block_index': 1, 'file_id':1, '_id': 0}))

    types_and_classes = combine_blocks(types_and_classes)
    #types_and_classes = [p for p in types_and_classes if p['block_index'] == 1]
    

    types_and_classes_preprocessed = [
            (preprocess(papyrus['training_text']), papyrus['grammateus_type'])  
            for papyrus in tqdm(types_and_classes)]
   
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
    write_to_disk(train_data, "train.json")
    write_to_disk(dev_data, "dev.json")
    write_to_disk(test_data, "test.json")


def test_dev_train_split(data_list, random_seed=42):

    random.Random(random_seed).shuffle(data_list)

    split_idx_test = int(len(data_list) * 0.1)
    split_idx_dev = int(len(data_list) * 0.2)
    train_data = data_list[split_idx_dev:]
    dev_data = data_list[split_idx_test:split_idx_dev]
    test_data = data_list[:split_idx_test]

    return train_data, dev_data, test_data

def write_to_disk(data, filename):
    disk_data = []
    
    for doc, label in data:
        cat = None
        cat = GRAMMATEUS_TYPES.index(label)
        if cat is None:
            print(f"Error: {label} is not a known label")
        disk_data.append({
            'label': cat,
            'text': doc
            })
    
    with open(filename, 'w') as f:
        json.dump(disk_data, f)

def combine_blocks(papyri_and_classes):
    first_blocks = [(papyrus, []) for papyrus in papyri_and_classes if papyrus['block_index'] == 1]
    other_blocks = [papyrus for papyrus in papyri_and_classes if papyrus['block_index'] > 1]

    for other_block in other_blocks:
        for i in range(len(first_blocks)):
            if first_blocks[i][0]['file_id'] == other_block['file_id']:
                first_blocks[i][1].append(other_block)


    combined_blocks = []
    for first_block, next_blocks in first_blocks:
        if len(next_blocks) == 0:
            combined_blocks.append(first_block)
            continue

        next_blocks.sort(key=lambda papyrus: papyrus['block_index'])
        next_blocks_text = [block['training_text'] for block in next_blocks]

        combined_text = "\n\n".join([first_block['training_text'], *next_blocks_text])
        combined_block = first_block
        combined_block['training_text'] = combined_text
        combined_blocks.append(combined_block)

    return combined_blocks



def preprocess(training_text):
    #training_text = re.sub(r"[\[\]\(\)]", "", training_text)
    #training_text = re.sub(r"(\<gap\/\>)|(\.{2,})", " ", training_text)
    return training_text
    #joined_terms = " ".join(terms)
    #preprocessed_title = remove_punctuation_stopwords(title, nlp)
    #preprocessed_terms = remove_punctuation_stopwords(joined_terms, nlp)
    #return f"{preprocessed_title} {preprocessed_terms}"

#def remove_punctuation_stopwords(text, nlp: Language):
#    tokens = [token.text for token in nlp(text)]
#    tokens = [token for token in tokens if
#              token not in STOP_WORDS and
#              token not in string.punctuation and
#              len(token) > 3]
#
#    return " ".join(tokens)

if __name__=="__main__":
	main()
