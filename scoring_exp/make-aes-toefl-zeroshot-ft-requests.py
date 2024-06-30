import argparse
import json
import pandas as pd

# write a function to get dd:mm:yy of today
def get_today():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%m%d")

parser = argparse.ArgumentParser(description='Make AES TOEFL requests')
parser.add_argument('--bg-file', metavar='BG_FILE', type=str,
                    help='the background file')
parser.add_argument('--instruct-file', metavar='INSTRUCT_FILE', type=str,
                    help='the instructions file')
parser.add_argument('--prompt-dir', metavar='PROMPT_FILE', type=str,
                    help='the prompt file')
parser.add_argument('--model-id', type=str, required=True)
parser.add_argument('--metadata', type=str, required=True)
parser.add_argument('--index-file', type=str, required=True, help='index dir')
parser.add_argument('--essay-dir', metavar='ESSAY_DIR', type=str,
                    help='the essay directory')
# add a store_true argument for the --include-prompt flag
parser.add_argument('--include-prompt', dest='include_prompt', action='store_true',
                    help='include the prompt in the output')
args = parser.parse_args()

# Read the background file, all text in a single string
with open(args.bg_file, 'r') as f:
    background = f.read()
    
# Read the instructions file, all text in a single string
with open(args.instruct_file, 'r') as f:
    instruction = f.read()
    
# Read list of prompts from files under the prompt directory
prompt_map = {}
for i in range(1, 9):
    with open(f"{args.prompt_dir}/P{i}.txt", 'r') as f:
        prompt_map[f"P{i}"] = f.read()
    

index_df = pd.read_csv(args.index_file)

# 添加新的表头
# new_headers = ['file_id', 'prompt', 'score_level']
# index_df.columns = new_headers
# print(index_df.head())

request_list = []
for index, row in index_df.iterrows():
    
    file_id = row['file_id']
    prompt = row['prompt']
    
    with open(f"{args.essay_dir}/{file_id}", "r") as f:
        essay = f.read()
    
    essay_prompt = prompt_map[prompt]
    
    if args.include_prompt:
        final_instruction = instruction.format(essay_prompt, essay)
    else:
        final_instruction = instruction.format(essay)
    
    messages = [{"role": "system", "content": background}, {
        "role": "user", "content": final_instruction}]
    response_format = {"type": "json_object"}
    request = {"model": args.model_id, "messages": messages,
                "response_format": response_format, 
                "seed": 42, 
                "temperature": 0, 
                "max_tokens": 64,
                "metadata": {"essay_id": file_id}}
    request_list.append(request)
    
output_file = f"requests/aes_for_cfact/TOEFL11/ft-gpt-3.5-turbo-1106/request_plus_prompt_{args.metadata}_{get_today()}.jsonl"
    
# save the request list to a file
with open(output_file, "w", encoding="utf-8") as f:
    for json_obj in request_list:
        f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")