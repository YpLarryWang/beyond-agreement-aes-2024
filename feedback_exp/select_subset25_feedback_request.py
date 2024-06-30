# 首先遍历所有的intervention startegy
# 然后根据`feedback_exp/subset_index_for_feedback`下面的8个和strategy对应的index文件，读取其中的text_id
# 然后根据text_id从`requests/fewshot_with_feedback/ELL/gpt-4-1106-preview`下面对应的200个样本的request文件中选择与这些text_id对应的requests
# 分别将读取到的requests存储为前缀为subset25的jsonl文件，准备进行api调用

import json
import os
import pandas as pd


intervention_strategy_list = [
    "error_introduction_in_sentence_spelling_0120",
    "error_introduction_in_sentence_sva_0120",
    "error_introduction_in_sentence_word_order_0120",
    "error_introduction_paragraph_0120",
    "error_introduction_discourse_0120",
    "error_correction_0113",
    "overall_simplification_0113",
    "overall_enhancement_0113",
]

index_base_path = "feedback_exp/subset_index_for_feedback/"
request_base_path = "requests/feedback/ELLIPSE/fewshot"

for strategy in intervention_strategy_list:
    index_file_path = os.path.join(index_base_path, "index_" + strategy + "_subset25.jsonl")
    request_file_path = os.path.join(request_base_path, "subset200_" + strategy + "_gpt-4-1106-preview_0127.jsonl")
    
    index_df = pd.read_json(index_file_path, lines=True)
    index_text_id_list = index_df['text_id'].tolist()
    
    subset25_request_list = []
    with open(request_file_path, "r") as f:
        request_list = [json.loads(line) for line in f.readlines()]
        
        for request in request_list:
            print(type(request))
            print(request)
            # print(len(request))
            # print(request[-1])
            if request['metadata']['essay_id'] in index_text_id_list:
                subset25_request_list.append(request)
    
    # 将subset25_request_list写入到文件中
    subset25_request_file_path = os.path.join(request_base_path, "subset25_" + strategy + "_gpt-4-1106-preview_0127.jsonl")
    with open(subset25_request_file_path, "w") as f:
        for request in subset25_request_list:
            f.write(json.dumps(request, ensure_ascii=False) + "\n")
    
    print("Finished", strategy)