import sys
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加该目录到 sys.path
sys.path.append(current_dir)

import argparse

import pandas as pd
import spacy
from lemminflect import getInflection

from error_simulator import ErrorSimulator


# write a function to get dd:mm:yy of today
def get_today():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%m%d")


parser = argparse.ArgumentParser()
parser.add_argument('--input-file', type=str)
parser.add_argument('--output-dir', type=str)
parser.add_argument('--id-col', type=str, required=True)
parser.add_argument('--text-col', type=str, required=True)
parser.add_argument('--debug', action="store_true")
parser.add_argument('--no-debug', action="store_true")
args = parser.parse_args()

df = pd.read_json(args.input_file, lines=True)

if args.debug:
    df = df.head()

# 加载 Spacy 英语模型
nlp = spacy.load("en_core_web_sm")

# df[args.id_col] = df[args.id_col].apply(lambda x: str(x) + '.txt')

random_seed = 42

error_simulator = ErrorSimulator(nlp, error_rate=0.5, seed=random_seed)

for intervention_level in ["in_sentence", "paragraph", "discourse"]:
    print(intervention_level)
    if intervention_level == 'in_sentence':
        for in_sent_mode in ["spelling", "sva", "word_order"]:
            
            print(f'\t{in_sent_mode}')
            
            # for idx, row in df.iterrows():
            #     print(row['file_id'])
            #     error_simulator.introduce_errors(row['text'], intervention_level, in_sent_mode)
            
            df[f"text_by_{random_seed}"] = df[args.text_col].apply(
                error_simulator.introduce_errors, args=(intervention_level, in_sent_mode, ))
            df_temp = df[[args.id_col, f"text_by_{random_seed}"]].copy()
            df_temp.loc[:, "text"] = df_temp[f"text_by_{random_seed}"]
            df_temp = df_temp.drop(columns=[f"text_by_{random_seed}"])

            df_temp.to_json(
                f"{args.output_dir}/error_introduction_{intervention_level}_{in_sent_mode}_{get_today()}_counterfactuals.jsonl",
                orient='records',
                lines=True)
    else:
        df[f"text_by_{random_seed}"] = df[args.text_col].apply(
            error_simulator.introduce_errors, args=(intervention_level, ))
        df_temp = df[[args.id_col, f"text_by_{random_seed}"]].copy()
        df_temp.loc[:, "text"] = df_temp[f"text_by_{random_seed}"]
        df_temp = df_temp.drop(columns=[f"text_by_{random_seed}"])

        df_temp.to_json(
            f"{args.output_dir}/error_introduction_{intervention_level}_{get_today()}_counterfactuals.jsonl",
            orient='records',
            lines=True)
