import pymongo
import re
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained('bowphs/GreBerta')
model = AutoModelForMaskedLM.from_pretrained('bowphs/GreBerta')

#test_text = """λοιπὸν <mask> τὰ παρόντα γράμματα"""

def try_fill_mask(model, tokenizer, input_text):
    inputs = tokenizer(input_text ,return_tensors='pt').to(model.device)


    with torch.no_grad():
        outputs = model(**inputs)
        predictions = outputs.logits

    masked_index = torch.where(inputs['input_ids'] == tokenizer.mask_token_id)[1]
    predicted_token_id = predictions[0, masked_index].argmax(dim=-1)
    predicted_token = tokenizer.decode(predicted_token_id)

    return predicted_token

def test_case_to_mask(test_case):
   return re.sub(r"\[.*?\]", "<mask>", test_case)

client = pymongo.MongoClient()
collection = client.get_database("stage-work").get_collection("MAAT")

def fetch_example_from_db(tm_id):
    example = collection.find_one({"tm_id":str(tm_id)}, {"test_cases": 1, "training_text": 1})
    return example

example_tm_id = 19822

example = fetch_example_from_db(example_tm_id)

for test_case in example["test_cases"]:
    test_case_text = test_case["test_case"]
    print("#-------------------------------------------#")
    print(test_case_text)
    masked_input = test_case_to_mask(test_case_text)
    print(masked_input)
    model_inference = try_fill_mask(model, tokenizer, masked_input)
    print(f"Model guess: {model_inference}") 
