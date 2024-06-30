import json
import os
import argparse
import re


def parse_results(results_dir):
    """
    parse the results file and return a list of dictionaries, each dictionary contains the result of each request.
    """
    
    success_list = []
    manual_list = []

    with open(results_dir, "r") as f_in:
        
        lines = f_in.readlines()
        for _, line in enumerate(lines):

            line = json.loads(line)
            
            bad = False

            request = line[0]
            response = line[1]
            metadata = line[2]
            
            parsed_response = response['choices'][0]['message']['content']

            # use regular expression to extract the JSON part
            pattern = r'{.*?}'
            match = re.search(pattern, parsed_response, re.DOTALL)

            if match:
                json_part = match.group()
                parsed_response = json.loads(json_part)[args.score_field]
            else:
                bad = True
                print("No JSON found")
                            
            metadata[args.score_field] = parsed_response
            success_list.append(metadata)
            
            if bad:
                manual_list.append(metadata)

        return success_list, manual_list


# make argparse
parser = argparse.ArgumentParser()
parser.add_argument('--request_file', type=str, help='Request file')
parser.add_argument('--api_output', type=str, help='API output file')
parser.add_argument('--score_field', type=str, help='Score field', required=True)
args = parser.parse_args()

# read requests
with open(args.request_file, "r", encoding="utf-8") as f:
    requests = [json.loads(line) for line in f.readlines()]

# parse the results file
success_list, manual_list = parse_results(args.api_output)

# 将结果写入文件jsonl
output_file = os.path.dirname(args.api_output) + '/SUCCESS_' + os.path.basename(args.api_output)
with open(output_file, 'w') as f:
    for item in success_list:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
print('Successfullly parsed the output file: ', output_file)

filter_prompt_file = 'prompts/filter/prompt_for_scoring.txt'
with open(filter_prompt_file, 'r') as f:
    filter_prompt = f.read()

error_file = os.path.dirname(args.api_output) + '/ERROR_' + os.path.basename(args.api_output)

# write those requests that need manual check to a file
with open(error_file, 'w') as error_f:
    for item in manual_list:
        
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {
        "role": "user", "content": f"{filter_prompt.format(item[args.score_field])}"}]
        item.pop(args.score_field)
        request = {
            "model": "gpt-3.5-turbo-0125",
            "messages": messages,
            "response_format": {"type": "json_object"},
            "seed": 42,
            "temperature": 0,
            "max_tokens": 24,
            "metadata": item}
        
        error_f.write(json.dumps(request, ensure_ascii=False) + '\n')

print('Those requests that need manual check are saved in: ', error_file)
        
