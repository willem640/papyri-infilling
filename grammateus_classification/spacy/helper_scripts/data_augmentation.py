import random 

# adapted from: https://github.com/ericu9500/PapyriAndInscriptions/blob/master/train_data/12_prepare_train_text_2.py
def randomly_remove_characters(text: str, p: float):
    characters = list(text)
    indices_to_replace = [i for i, c in enumerate(characters) if c not in ('-', ' ', '…', '·', '.', '[', ']')]

    num_to_replace = int(len(indices_to_replace) * p)
    chosen_indices = random.sample(indices_to_replace, num_to_replace)

    for i in chosen_indices:
        characters[i] = '.'

    return ''.join(characters)

