import argparse
import json

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def write_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')

def process_files(jsonl_path, mapping_path, output_path):
    # 读取映射文件
    id_mapping = read_json(mapping_path)
    
    # 读取原始JSONL文件
    data = read_jsonl(jsonl_path)
    
    # 进行映射和添加新key-value
    for entry in data:
        text_id_kaggle = entry.get('text_id_kaggle')
        if text_id_kaggle in id_mapping:
            entry['text_id'] = id_mapping[text_id_kaggle]
        else:
            entry['text_id'] = text_id_kaggle
    
    # 写入新的JSONL文件
    write_jsonl(data, output_path)

def main():
    parser = argparse.ArgumentParser(description='Process JSONL file with text_id_kaggle mappings.')
    parser.add_argument('--jsonl_path', type=str, help='Path to the original JSONL file')
    parser.add_argument('--mapping_path', type=str, help='Path to the JSON mapping file')
    parser.add_argument('--output_path', type=str, help='Path to the output JSONL file')

    args = parser.parse_args()
    
    process_files(args.jsonl_path, args.mapping_path, args.output_path)

if __name__ == '__main__':
    main()