import pymongo
from os import environ
from pathlib import Path
from tqdm import tqdm

from pyepidoc import EpiDoc

from helpers.ddbdp_id_exceptions import get_exception 


# Note: this only finds about 5/6 of the MAAT papyri. Remains a WIP
def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    duke_databank_epidocs = environ.get("DUKE_DATABANK_EPIDOCS", "idp.data/DDB_EpiDoc_XML")

    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)
    for ddbdp_epidoc in tqdm(Path(duke_databank_epidocs).rglob("*.xml")):
        doc = EpiDoc(ddbdp_epidoc)
        idnos = doc.file_desc.publication_stmt.idnos
        # get first (in this case only) idno with type "filename", which will be the same as the file_id in MAAT
        try:
            ddbdp_idno = next(idno.value for idno in idnos if idno.type == "filename") 
        except StopIteration:
            print(f"File does not have a filename: {idnos}")
            continue
        ddbdp_idno = get_exception(ddbdp_idno) # sometimes the id in MAAT/papyri.info can be different so we need to translate between them 
        tm_idno = next((idno.value for idno in idnos if idno.type == "TM"), None) # If no TM id is available, just don't set it for now, TODO 
        hgv_idno = next((idno.value for idno in idnos if idno.type == "HGV"), None) 
        collection.update_many({'file_id': ddbdp_idno}, {'$set': {'tm_id': tm_idno, 'hdv_id': hgv_idno}})

if __name__=="__main__":
    main()
