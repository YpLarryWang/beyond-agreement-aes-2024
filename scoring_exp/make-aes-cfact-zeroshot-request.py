import argparse
import json
import os
import pandas as pd


parser = argparse.ArgumentParser(
    description='Make AES requests for all dataset')
parser.add_argument('--model-id', type=str, required=True)
parser.add_argument('--prompt-dir', metavar='PROMPT_FILE', type=str,
                    help='the prompt file')
parser.add_argument('--essay-dir', metavar='ESSAY_DIR', type=str,
                    help='the essay directory')
parser.add_argument('--id-field', metavar='ID_FIELD',
                    type=str, required=True, help='the id field')
parser.add_argument('--text-field', metavar='TEXT_FIELD',
                    type=str, required=True, help='the text field')
parser.add_argument('--output-file', metavar='OUTPUT_FILE',
                    type=str, required=True, help='the output file')
parser.add_argument('--dataset', type=str, required=True, help='dataset')
parser.add_argument('--fine-tune', action='store_true', help='fine tune')
args = parser.parse_args()

# Read the background file, all text in a single string
with open(f"{args.prompt_dir}/system.txt", 'r') as f:
    background = f.read()

# Read the instructions file, all text in a single string
if args.fine_tune:
    with open(f"{args.prompt_dir}/user_message_ft.txt", 'r') as f:
        instruction = f.read()
else:
    with open(f"{args.prompt_dir}/user_message_zsl.txt", 'r') as f:
        instruction = f.read()

if args.dataset == "TOEFL11":
    with open(f"{args.prompt_dir}/essay_prompt/test_id_map.json", 'r') as f:
        id_to_prompt = json.load(f)

    prompt_map = {}
    for i in range(1, 9):
        with open(f"{args.prompt_dir}/essay_prompt/P{i}.txt", 'r') as f:
            prompt_map[f"P{i}"] = f.read()

dataframe = pd.read_json(args.essay_dir, lines=True)

request_list = []
for index, row in dataframe.iterrows():

    row_id = row[args.id_field]
    essay = row[args.text_field]

    if args.dataset == "TOEFL11":
        prompt = id_to_prompt[row_id]
        essay_prompt = prompt_map[prompt]
        final_instruction = instruction.format(essay_prompt, essay)
    elif args.dataset == "ELLIPSE":
        final_instruction = instruction.format(essay)
    else:
        raise ValueError("Invalid dataset")

    messages = [{"role": "system", "content": background}, {
        "role": "user", "content": final_instruction}]
    response_format = {"type": "json_object"}
    request = {"model": args.model_id, "messages": messages,
               "response_format": response_format,
               "seed": 42,
               "temperature": 0,
               "max_tokens": 64,
               "metadata": {args.id_field: row_id}}
    request_list.append(request)

os.makedirs(os.path.dirname(args.output_file), exist_ok=True)

# save the request list to a file
with open(args.output_file, "w", encoding="utf-8") as f:
    for json_obj in request_list:
        f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")