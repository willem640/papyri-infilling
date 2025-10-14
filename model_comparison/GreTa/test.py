from transformers import AutoTokenizer, T5ForConditionalGeneration 
import pymongo
import re


tokenizer = AutoTokenizer.from_pretrained('bowphs/GreTa')
model = T5ForConditionalGeneration.from_pretrained('bowphs/GreTa')

extra_ids = [f"<extra_id_{i}>" for i in range(100)]

tokenizer.add_special_tokens({"additional_special_tokens": extra_ids})
#test_text = """λοιπὸν δεχόμενος τὰ παρόντα γράμματα"""
test_text = """λοιπὸν δεχόμενος<extra_id_0> παρόντα γράμματα"""
test_labels = """<extra_id_0> τὰ "<extra_id_1>"""

def try_fill_mask(model, tokenizer, masked_input, num_results=5):
    input_ids = tokenizer(masked_input, return_tensors="pt", add_special_tokens=True).input_ids

#    for inp_id in input_ids[0]:
#        print(tokenizer.decode(inp_id))
    outputs = model.generate(input_ids, num_beams=2 * num_results, num_return_sequences=num_results, diversity_penalty=1.5)
    
    text_outputs = [tokenizer.decode(output) for output in outputs]
    infillings = []
    for text_output in text_outputs:
        matches = re.findall(r"<extra_id_\d>(.*?)(?=<extra_id_\d>)", text_output) 
        infillings.append(matches)
    
    return infillings


def test_case_to_mask(test_case):
    test_case = re.sub(r"<gap\/>", "", test_case)
    return re.sub(r"\[.*?\]", "<extra_id_0>", test_case)

def train_text_convert(training_text):
    # remove <gap/> for now
    training_text = re.sub(r"<gap\/>", "", training_text)
    match_n = 0
    while True:
        training_text, number_of_subs_made = re.subn(r"\[.*?\]", f"<extra_id_{match_n}>", training_text, count=1)
        match_n += 1
        # Do at most one substitution, and increment the extra_id number every loop
        if number_of_subs_made == 0:
            break
    return training_text
    

client = pymongo.MongoClient()
collection = client.get_database("stage-work").get_collection("MAAT")

def fetch_example_from_db(tm_id):
    example = collection.find_one({"tm_id":str(tm_id)}, {"test_cases": 1, "training_text": 1})
    return example

example_tm_id = 25288

example = fetch_example_from_db(example_tm_id)

train_text = train_text_convert(example["training_text"])
print("#----------------TRAIN TEXT------------------#")
print(train_text)
print(try_fill_mask(model, tokenizer, train_text))

for test_case in example["test_cases"]:
    test_case_text = test_case["test_case"]
    print("#------------------TEST CASES------------------#")
    print(test_case_text)
    masked_input = test_case_to_mask(test_case_text)
    print(masked_input)
    model_inference = try_fill_mask(model, tokenizer, masked_input)
    print(f"Model guess: {model_inference}") 
