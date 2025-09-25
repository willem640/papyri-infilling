import pymongo
import argparse
import json
from tqdm import tqdm

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--database", required=True)
    arg_parser.add_argument("--mongo_database", required=True)
    arg_parser.add_argument("--mongo_collection", required=True)

    args = arg_parser.parse_args()
    
    client = pymongo.MongoClient()
    collection = client.get_database(args.mongo_database).get_collection(args.mongo_collection)
    
    papyri_dataset = []
    with open(args.database) as f:
        for line in tqdm(f):
            papyri_dataset.append(json.loads(line))

    
    for papyrus in tqdm(papyri_dataset):
        # Ignore Latin texts and ignore anything that isn't a papyrus (ostrakon, wood, etc)
        if papyrus["language"] != "grc" or papyrus["material"] != "papyrus":
            continue
        try:
            collection.insert_one(papyrus)
        except Exception as e:
            id = papyrus["corpus_id"] + " " + papyrus["file_id"]
            print(f"Problematic papyrus: {id}, insert caused an exception: {e}")


if __name__=="__main__":
    main()
