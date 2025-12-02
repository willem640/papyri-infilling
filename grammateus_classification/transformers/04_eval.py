import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding
from datasets import load_dataset
import evaluate
import numpy as np

MODEL_PATH = "model/checkpoint-1000"
GRAMMATEUS_TYPES = ["Epistolary Exchange", "Transmission of Information", "Objective Statement", "Recording of Information"]

def main():
    data = load_dataset("json", data_files={'test':'test.json'})

    tokenizer = AutoTokenizer.from_pretrained('bowphs/GreBerta')

    tokenized_data = data.map(lambda papyrus: tokenizer(papyrus['text'], truncation=True, max_length=512), batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    label2id = {label: GRAMMATEUS_TYPES.index(label) for label in GRAMMATEUS_TYPES}
    id2label = {idno: label for label, idno in label2id.items()}

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=len(GRAMMATEUS_TYPES), id2label=id2label, label2id=label2id)

    tokenized_data = tokenized_data.remove_columns(data["test"].column_names)

    loader = torch.utils.data.DataLoader(tokenized_data['test'].with_format('torch'), batch_size=32, collate_fn=data_collator) 


    predictions = []
    for batch in loader:
        predictions_batch = model(**batch)
        predictions.extend(predictions_batch['logits'])


    predictions = [tensor.cpu().detach() for tensor in predictions]

    predictions_and_labels = (predictions, list(data['test']['label']))

    metrics = compute_metrics(predictions_and_labels)

    print(f"Eval: {metrics}")





metric=evaluate.load('f1')
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    return metric.compute(predictions=predictions, references=labels, average='macro')

if __name__=="__main__":
    main()
