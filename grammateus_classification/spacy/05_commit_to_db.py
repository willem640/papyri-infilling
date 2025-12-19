import json
from os import environ

import pymongo
from tqdm import tqdm

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
   
    with open('./papyri_with_classes.json') as all_papyri_f, open('./checked_papyri.json') as manual_papyri_f:
        all_papyri = json.load(all_papyri_f)
        manual_papyri = json.load(manual_papyri_f)
    
    combined_papyri = combine(all_papyri, manual_papyri)
    
    for papyrus in tqdm(combined_papyri):
        collection.update_many({'tm_id': papyrus['tm_id']},
                               {'$set': {'grammateus_type': papyrus['grammateus_type']}})

def combine(all_papyri, manual_papyri):
    all_combined = []
    for papyrus in all_papyri:
        for manual_papyrus in manual_papyri:
            if papyrus['tm_id'] == manual_papyrus['file_id']:
                papyrus['grammateus_type'] = manual_papyrus['grammateus_type']
        all_combined.append(papyrus)
    return all_combined


if __name__=="__main__":
    main()
