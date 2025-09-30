from os import environ
import pymongo
import json
from tqdm import tqdm

def main():
    maat_filename = environ.get("MAAT_FILENAME", "maat.json")
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    
    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    
    papyri_dataset = []
    with open(maat_filename) as f:
        for line in tqdm(f):
            papyri_dataset.append(json.loads(line))

    
    for papyrus in tqdm(papyri_dataset):
        # Ignore Latin texts and ignore anything that isn't a papyrus (ostrakon, wood, etc)
        if papyrus["language"] != "grc" or papyrus["material"] != "papyrus" or papyrus["corpus_id"] == "DCLP":
            continue
        try:
            collection.insert_one(papyrus)
        except Exception as e:
            id = papyrus["corpus_id"] + " " + papyrus["file_id"]
            print(f"Problematic papyrus: {id}, insert caused an exception: {e}")


if __name__=="__main__":
    main()
