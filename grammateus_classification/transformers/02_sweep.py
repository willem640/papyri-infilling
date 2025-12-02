from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding, EarlyStoppingCallback, Trainer, TrainingArguments, training_args
from datasets import load_dataset
import evaluate
import numpy as np
import os
import wandb

GRAMMATEUS_TYPES = ["Epistolary Exchange", "Transmission of Information", "Objective Statement", "Recording of Information"]

def main():
    os.environ["WANDB_PROJECT"] = "papyri-infilling-transformers" 

    run = wandb.init()

    data = load_dataset("json", data_files={'train': 'train.json', 'validation':'dev.json'})

    tokenizer = AutoTokenizer.from_pretrained('bowphs/GreBerta')

    tokenized_data = data.map(lambda papyrus: tokenizer(papyrus['text'], truncation=True, max_length=512), batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    label2id = {label: GRAMMATEUS_TYPES.index(label) for label in GRAMMATEUS_TYPES}
    id2label = {idno: label for label, idno in label2id.items()}
    
    model = AutoModelForSequenceClassification.from_pretrained('bowphs/GreBerta', num_labels=len(GRAMMATEUS_TYPES), id2label=id2label, label2id=label2id,
            hidden_dropout_prob=run.config['dropout'],
            attention_probs_dropout_prob=run.config['dropout'])

    training_args = TrainingArguments(
        output_dir='model',
        learning_rate=run.config['learning_rate'],
        lr_scheduler_type='cosine_with_min_lr',
        lr_scheduler_kwargs = {
          'min_lr_rate': run.config['min_learning_ratio'],
        },
        max_steps=run.config['max_steps'],
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        #num_train_epochs=50,
        weight_decay=1e-5,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_data['train'],
        eval_dataset=tokenized_data['validation'],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=run.config['patience'])]
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

    return metric.compute(predictions=predictions, references=labels, average='macro')

if __name__=="__main__":
    main()
