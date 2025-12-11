from os import environ
from typing import Dict

import json
from tqdm import tqdm

from importlib import import_module

prepare_data = import_module('01_prepare_data')

def main():
    with open('03_cats.json') as f:
        all_cats = json.load(f)

    with open('03_first_blocks.json') as f:
        first_blocks = json.load(f)

    with open('03_other_blocks.json') as f:
        other_blocks = json.load(f)

    first_blocks_processed = [{'grammateus_type': grammateus_type, **papyrus} for grammateus_type, papyrus in zip(all_cats, first_blocks)]

    combined_blocks = prepare_data.combine_blocks([*first_blocks_processed, *other_blocks]
    
    with open('papyri_with_classes.json', 'w') as f:
        json.dump(combined_blocks, f)
        

if __name__=="__main__":
    main()
