import argparse
import json
import os

# write a function to get dd:mm:yy of today
def get_today():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%m%d")

parser = argparse.ArgumentParser()
parser.add_argument('--feedback-instruct', metavar='FEEDBACK_FILE', type=str,
                    help='the feedback instructions file')
parser.add_argument('--last-turn-file', metavar='LASTTURN_FILE', type=str,
                    help='the last turn file')
parser.add_argument('--output-file', metavar='OUTPUT_FILE', type=str,
                    help='the output file')
args = parser.parse_args()

os.makedirs(os.path.dirname(args.output_file), exist_ok=True)

# Read the feedback file, all text in a single string
with open(args.feedback_instruct, 'r') as f:
    feedback_instruct = f.read()
    
# Read the last turn file (jsonl, openai format)
with open(args.last_turn_file, 'r') as f:
    last_turn = [json.loads(line) for line in f.readlines()]

model_id = last_turn[0][0]['model']

request_list = []
for record in last_turn:
    
    messages = record[0]['messages']
    messages.append(record[1]['choices'][0]['message'])
    messages.append({
        "role": "user", "content": feedback_instruct
    })
    
    response_format = {"type": "json_object"}
    
    request = {"model": record[0]['model'], "messages": messages,
                "response_format": response_format, 
                "seed": 42, 
                "temperature": 0, 
                "max_tokens": 2048,
                "metadata": record[2]}
    request_list.append(request)
    
print(args.output_file)
    
# save the request list to a file
with open(args.output_file, "w", encoding="utf-8") as f:
    for json_obj in request_list:
        f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")