from pyepidoc.xml.errors import handle_xmlsyntaxerror
import pymongo
import re
from os import environ
from pathlib import Path
from tqdm import tqdm

from pyepidoc import EpiDoc

# TODO what if there are multiple places?

def main():
    mongo_database = environ.get("MONGO_DATABASE", "papyri")
    mongo_collection = environ.get("MONGO_COLLECTION", "maat")
    hgv_epidocs = environ.get("HGV_EPIDOCS", "idp.data/HGV_meta_EpiDoc")

    client = pymongo.MongoClient()
    collection = client.get_database(mongo_database).get_collection(mongo_collection)

    for hgv_epidoc in tqdm(list(Path(hgv_epidocs).rglob("*.xml"))):
        doc = EpiDoc(hgv_epidoc)
        idnos = doc.file_desc.publication_stmt.idnos
              
        try:
            hgv_idno = next(idno.value for idno in idnos if idno.type == "filename") 
        except StopIteration:
            print(f"File does not have a filename: {idnos}")
            continue
        orig_place = get_location(doc)
        date_range = doc.daterange
        text_classes = get_text_classes(doc)
        update = {
            'orig_place': orig_place,
            'text_classes': text_classes
        }
        if date_range is not None and date_range != (None, None):
            update['date_range'] = {'min': date_range[0], 'max': date_range[1]}
        collection.update_many(
                {'hgv_id' : hgv_idno }, \
                        {'$set': update})

def get_text_classes(doc):
    text_classes = doc.xpath('//ns:textClass/ns:keywords[@scheme="hgv"]/ns:term/text()')
    return text_classes

def get_location(doc):
    # HGV has a provenance section with a trismegistos places reference, which is better than the string name provided by doc.orig_place
    # use xpath + regex to get it out, but fall back to pleiades or string name when trismegistos is not provided

    result = {}

    provenance_tm_xpath = '//ns:history/ns:provenance/ns:p/ns:placeName[@type="ancient" and @subtype="nome"]'
    provenance = doc.xpath(provenance_tm_xpath)
    if len(provenance) > 0:
        # EpiDoc has a section with a trismegistos and/or pleiades reference
        place_name = provenance[0]
        urls = place_name.get("ref")
        if urls is not None and len(urls) > 0:
            tm_place_id_regex = r"https:\/\/www\.trismegistos\.org\/place\/(\d+)"
            pleiades_id_regex = r"https:\/\/pleiades\.stoa\.org\/places\/(\d+)"
            if tm_id := re.match(tm_place_id_regex, urls):
                result['TM'] = tm_id.group(1)
            if pl_id := re.match(pleiades_id_regex, urls):
                result['PL'] = pl_id.group(1)
            if place_name.text != None:
                result['text'] = place_name.text
    
    # If none of these methods worked, try getting the "normal" placeName
    # EpiDoc.orig_place wants [@type="ancient"] set, but this is not the case in the HGV EpiDocs
    if 'text' not in result:
        orig_places = doc.get_desc('origPlace')
        if len(orig_places) > 0:
            result['text'] = orig_places[0].text # just take the first one if there are multiple
    return result

            



if __name__=="__main__":
    main()
