from os import environ
from typing import Dict

import json
from tqdm import tqdm

import spacy
spacy.prefer_gpu()

def main():
    classifier = spacy.load('model/model-best')
    classifier_input = []
    with open('03_classifier_input') as f:
        classifier_input = json.load(f)

    all_cats = []
    for doc in tqdm(classifier.pipe(classifier_input)):
        cat = get_cat(doc.cats)

        all_cats.append(cat)

    with open('03_cats.json', 'w') as f:
        json.dump(all_cats, f)
        
def get_cat(cats: Dict[str, float]):
    max_score = 0
    max_cat = None
    for cat, score in cats.items():
        if score > max_score:
            max_score = score
            max_cat = cat
    
    return max_cat

if __name__=="__main__":
    main()
