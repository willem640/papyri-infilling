from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding, EarlyStoppingCallback, Trainer, TrainingArguments, training_args
from datasets import load_dataset
import evaluate
import numpy as np

GRAMMATEUS_TYPES = ["Epistolary Exchange", "Transmission of Information", "Objective Statement", "Recording of Information"]

def main():
    data = load_dataset("json", data_files={'train': 'train.json', 'validation':'dev.json'})

    tokenizer = AutoTokenizer.from_pretrained('bowphs/GreBerta')

    tokenized_data = data.map(lambda papyrus: tokenizer(papyrus['text'], truncation=True, max_length=512), batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    label2id = {label: GRAMMATEUS_TYPES.index(label) for label in GRAMMATEUS_TYPES}
    id2label = {idno: label for label, idno in label2id.items()}
    
    model = AutoModelForSequenceClassification.from_pretrained('bowphs/GreBerta', num_labels=len(GRAMMATEUS_TYPES), id2label=id2label, label2id=label2id)

    training_args = TrainingArguments(
        output_dir='model',
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_data['train'],
        eval_dataset=tokenized_data['test'],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
    )
    
    trainer.train()
    evaluation = trainer.evaluate()
    print(f"Eval: {evaluation}")
    trainer.save_model()


# TODO more metrics?
metric=evaluate.load('f1')
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    return metric.compute(predictions=predictions, references=labels)

if __name__=="__main__":
    main()
