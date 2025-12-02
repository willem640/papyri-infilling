import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding
from datasets import load_dataset
import evaluate
import numpy as np

MODEL_PATH = "model/checkpoint-1000"
GRAMMATEUS_TYPES = ["Epistolary Exchange", "Transmission of Information", "Objective Statement", "Recording of Information"]

def main():
    data = load_dataset("json", data_files={'data':'all_unlabeled.json'})

    tokenizer = AutoTokenizer.from_pretrained('bowphs/GreBerta')

    tokenized_data = data.map(lambda papyrus: tokenizer(papyrus['text'], truncation=True, max_length=512), batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    label2id = {label: GRAMMATEUS_TYPES.index(label) for label in GRAMMATEUS_TYPES}
    id2label = {idno: label for label, idno in label2id.items()}

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=len(GRAMMATEUS_TYPES), id2label=id2label, label2id=label2id)

    tokenized_data = tokenized_data.remove_columns(data["data"].column_names)

    loader = torch.utils.data.DataLoader(tokenized_data['data'].with_format('torch'), batch_size=32, collate_fn=data_collator) 


    predictions = []
    for batch in loader:
        predictions_batch = model(**batch)
        predictions.extend(predictions_batch['logits'])


    predictions = [get_cat(tensor.cpu().detach(), id2label) for tensor in predictions]


    all_papyri_processed = [{'grammateus_type': grammateus_type, **papyrus} for grammateus_type, papyrus in zip(predictions, list(data['data']['meta']))]

    with open('papyri_with_classes', 'w') as f:
        json.dump(all_papyri_processed, f)



def get_cat(prediction, id2label):
    cat = np.argmax(prediction)
    return id2label[cat]

if __name__=="__main__":
    main()
