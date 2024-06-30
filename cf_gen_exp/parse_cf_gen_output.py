import json
import re
from rapidfuzz import fuzz

# 使用正则表达式处理嵌入的引号
def fix_quotes(input_string):
    # 匹配键值之间的内容，并处理其中的引号
    pattern = re.compile(r'(?<=": ").*(?=")')
    match = pattern.search(input_string)
    if match:
        value = match.group(0)
        # 仅处理未转义的引号
        fixed_value = re.sub(r'(?<!\\)"', r'\\"', value)
        input_string = input_string[:match.start()] + fixed_value + input_string[match.end():]
    return input_string


def clean_content(content):
    # Split the content by double newlines
    paragraphs = content.strip().split('\n\n')
    
    # Convert paragraphs to lowercase for fuzzy matching
    paragraphs_lower = [p.lower() for p in paragraphs]
    
    # Check for the unwanted phrases using fuzzy matching
    if paragraphs and fuzz.partial_ratio(paragraphs_lower[0], "here is the corrected essay:") > 80:
        paragraphs = paragraphs[1:]
        paragraphs_lower = paragraphs_lower[1:]
    if paragraphs and fuzz.partial_ratio(paragraphs_lower[-1], "let me know if you need any further assistance!") > 80:
        paragraphs = paragraphs[:-1]
        paragraphs_lower = paragraphs_lower[:-1]
    
    # Join the paragraphs back together
    cleaned_content = '\n\n'.join(paragraphs).strip()
    
    # Remove quote marks and backticks from the beginning and end of the content if they exist
    cleaned_content = cleaned_content.strip('"').strip('`')
    
    # print(cleaned_content)
    # print('----------------')
    
    # Try to match JSON using regular expression
    json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
    
    # print(json_match)
    
    if json_match:
        json_content = json_match.group().strip()
        # print(json_content)
        json_content = json_content.replace('{\n\"output_essay\"', '{"output_essay"')
        json_content = json_content.replace('\"\n}', '"}')
        
        # 将JSON字符串中的换行符替换为特定的占位符
        json_content = json_content.replace('\n\n', '\\n\\n')
        json_content = json_content.replace('\n', '')
        
        json_content = fix_quotes(json_content)
        
        # print(json_content)
        
        # json_content = json_content.replace('\\"', '\"')
        
        try:
            content_json = json.loads(json_content)
            if 'output_essay' in content_json:
                essay = content_json['output_essay']
                
                # 将essay中的占位符替换回换行符
                essay = essay.replace('\\n\\n', '\n\n')
                print(essay)
                return essay
        except json.JSONDecodeError:
            pass
    
    # If JSON is not contained, return the result of step 1
    return cleaned_content

def parse_and_store_jsonl(input_file, output_file, retry_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile, open(retry_file, 'w') as badfile:
        for line in infile:
            data = json.loads(line)
            
            # Extract the `choices` content
            try:
                choices_content = data[1]['choices'][0]['message']['content']
            except KeyError:
                # print(data[0])
                # print('----------------')
                # print(data[1])
                badfile.write(json.dumps(data[0]) + '\n')
                continue
                
            # Clean the content
            cleaned_content = clean_content(choices_content)
            
            # Get the file_id
            file_id = data[-1][id_field]
            
            # Create the output dictionary
            output_data = {
                id_field: file_id,
                "output_essay": cleaned_content
            }
            
            # Write the result to the new JSONL file
            outfile.write(json.dumps(output_data) + '\n')

if __name__ == "__main__":
    id_field = 'text_id_kaggle'
    
    input_file = 'results/cf_gen_202406/ELLIPSE/results_ELLIPSE_Meta-Llama-3-70B-Instruct-0611_overall_enhancement_deepinfra.jsonl'  # 输入文件名
    output_file = 'results/cf_gen_202406/ELLIPSE/CLEAN_results_ELLIPSE_Meta-Llama-3-70B-Instruct-0611_overall_enhancement_deepinfra.jsonl'  # 输出文件名
    
    # input_file = 'results/cf_gen_202406/ELLIPSE/test.jsonl'
    # output_file = 'results/cf_gen_202406/ELLIPSE/CLEAN_test.jsonl'
    
    retry_file = 'results/cf_gen_202406/ELLIPSE/BAD_results_ELLIPSE_Meta-Llama-3-70B-Instruct-0611_overall_enhancement_deepinfra.jsonl'  # 输出文件名
    parse_and_store_jsonl(input_file, output_file, retry_file)
