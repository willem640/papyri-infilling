from os import environ

import pymongo
import csv
from tqdm import tqdm

def main():
    grammateus_path = environ.get("GRAMMATEUS_CSV", "grammateus.csv")
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
   
    grammateus_tm_and_text_class = []

    with open(grammateus_path, newline='') as f:
        reader = csv.reader(f)
        heading = next(reader)
        tm_idx = heading.index('TM')
        type_idx = heading.index(' Type')
        for row in tqdm(reader):
            tm_id = row[tm_idx = row[type_idx]
            collection.update_one({'tm_id': tm_id}, {'$set': {'grammateus_type': grammateus_type}})

if __name__=="__main__":
    main()
