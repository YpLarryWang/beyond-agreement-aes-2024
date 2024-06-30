import json
import os
import pandas as pd
import argparse

# write a function to get dd:mm:yy of today


def get_today():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%m%d")


# 命令行参数读取
parser = argparse.ArgumentParser()
parser.add_argument('--model_id', type=str, required=True, help='model id')
parser.add_argument('--sys_msg_file', type=str,
                    required=True, help='system message file')
parser.add_argument('--user_msg_file', type=str,
                    required=True, help='user message template file')
parser.add_argument('--input_file', type=str, required=True, help='input file')
parser.add_argument('--output_dir', type=str,
                    required=True, help='output file')
parser.add_argument('--id_field', type=str, required=True, help='id field')
parser.add_argument('--text_field', type=str, required=True, help='text field')
parser.add_argument('--request_style', type=str,
                    required=True, help='request style')
parser.add_argument('--transformation', type=str,
                    required=True, help='transformation')
parser.add_argument('--dataset', type=str, required=True, help='dataset')
args = parser.parse_args()

# make output dir
os.makedirs(args.output_dir, exist_ok=True)

# read prompt from file
with open(args.sys_msg_file, 'r') as f:
    sys_msg = f.read()

with open(args.user_msg_file, 'r') as f:
    user_msg_template = f.read()

request_list = []
with open(args.input_file, 'r') as f:

    lines = f.readlines()

    for line in lines:
        line = json.loads(line)

        essay = line[args.text_field]
        record_id = line[args.id_field]
        messages = [{"role": "system", "content": sys_msg}, {
            "role": "user", "content": user_msg_template.format(essay)}]

        response_format = {"type": "json_object"}
        if args.request_style == 'groq':
            request = {"model": args.model_id, "messages": messages,
                       "seed": 42, "temperature": 0,
                       "max_tokens": 2048,
                       "metadata": {args.id_field: record_id}}
        else:
            request = {"model": args.model_id, "messages": messages,
                       "response_format": response_format,
                       "seed": 42, "temperature": 0,
                       "max_tokens": 2048,
                       "metadata": {args.id_field: record_id}}

        request_list.append(request)

if args.request_style == 'deepinfra':
    model_short_name = args.model_id.split('/')[-1]
else:
    model_short_name = args.model_id

# save the request list to a file
with open(f"{args.output_dir}/requests_{args.dataset}_{model_short_name}-{get_today()}_{args.transformation}_{args.request_style}.jsonl", "w", encoding="utf-8") as f:
    for json_obj in request_list:
        f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
