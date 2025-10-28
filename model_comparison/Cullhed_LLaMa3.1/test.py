import json
from transformers import pipeline, AutoTokenizer, LlamaForCausalLM
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
import torch
import warnings

from util import minimal_maat_to_llama_input
import pymongo

warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter in the checkpoint*")
model_id = "Ericu950/Papy_2_Llama-3.1-8B-Instruct_text"

device = 'cpu'

# with init_empty_weights():
#     model = LlamaForCausalLM.from_pretrained(model_id)


# model = load_checkpoint_and_dispatch(
#     model,
#     model_id,
#     device_map="auto",
#     offload_folder="offload",
#     offload_state_dict=True,
# )

tokenizer = AutoTokenizer.from_pretrained(model_id)

generation_pipeline = pipeline(
    "text-generation",
    model=model_id,
#    tokenizer=tokenizer,
    device_map=device,
)
client = pymongo.MongoClient()
collection = client.get_database("stage-work").get_collection("MAAT")

def fetch_example_from_db(tm_id):
    example = collection.find_one({"tm_id":str(tm_id)}, {"test_cases": 1, "training_text": 1})
    return example

tm_id = "140711"

example = fetch_example_from_db(tm_id)

test_cases = []
for i in range(20):
    papyrus_edition = minimal_maat_to_llama_input(example['training_text'], i)
    test_cases.append(papyrus_edition)

print(test_cases[0])

for gap_idx, papyrus_edition in enumerate(test_cases):
    system_prompt = "Fill in the missing letters in this papyrus fragment!"
    input_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": papyrus_edition},
    ]
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = generation_pipeline(
        input_messages,
        max_new_tokens=25,
        num_beams=30, # Set this as high as your memory will allow!
        num_return_sequences=10,
        early_stopping=True,
    )
    beam_contents = []
    for output in outputs:
        generated_text = output.get('generated_text', [])
        for item in generated_text:
            if item.get('role') == 'assistant':
                beam_contents.append(item.get('content'))
    print(f"\nSuggestions for gap {gap_idx}")
    for i, content in enumerate(beam_contents, start=1):
        print(f"Suggestion {i}: {content}")


