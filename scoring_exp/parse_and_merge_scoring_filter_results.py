"""
本脚本用于解析QWEN的输出文件，将其转换为jsonl格式
每一行是一个列表，列表中是3个json对象，分别是
1. 请求内容，包括模型名称、输入数据、参数
2. API返回结果，有两种情况：
 - 一种是正常反馈的，是一个key为output的字典，value还是一个字典，其中名为text的key对应的value是我们想要的
 - 另一种是出错了的，包括返回码（code）、返回信息（message）、请求编号（request_id)，我们需要把错误信息保存在另一个文件中去
3. metadata，是一个字典
"""

import json
import argparse
import os

parser = argparse.ArgumentParser(description='Parse API output')
parser.add_argument('--orig_result', type=str, help='Request file')
parser.add_argument('--api_output', type=str, help='API output file')
parser.add_argument('--id_field', type=str, help='Field name for ID in metadata')
parser.add_argument('--simple_merge', action='store_true', help='Replace the original result with the API output')
args = parser.parse_args()



if args.simple_merge:
    success_list = [json.loads(line) for line in open(args.api_output, 'r')]
else:
    success_list = []    
    with open(args.api_output, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            obj = json.loads(line)
            
            request = obj[0]
            response = obj[1]
            metadata = obj[2]
            
            metadata['score'] = json.loads(response['choices'][0]['message']['content'])['score']
            success_list.append(metadata)


# 打开原始结果文件，如果有metadata出现在success_list中，则使用success_list中的response替换原始结果文件中的response
with open(args.orig_result, 'r') as orig_f:
    orig_results = [json.loads(line) for line in orig_f]
    new_results = []
    for orig_result in orig_results:
        for success_item in success_list:
            # 要比较的是两者去除了response字段之后的部分
            # 这部分是metadata但没有叫做metadata的key
            # print(orig_result)
            # print(success_item)
            if orig_result[args.id_field] == success_item[args.id_field]:
                orig_result['score'] = success_item['score']
            
        new_results.append(orig_result)
        
# 将结果写入文件jsonl
output_file = os.path.dirname(args.orig_result) + '/CLEANED_' + os.path.basename(args.orig_result)
with open(output_file, 'w') as f:
    for item in new_results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f'Successful results written to {output_file}')