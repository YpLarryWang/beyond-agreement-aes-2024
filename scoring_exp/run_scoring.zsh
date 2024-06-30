#!/bin/zsh

# NOTE that in the paper we only present fewshot learning scoring results for gpt-4-1106-preview and Meta-Llama-3-70B-Instruct on a stratified sampled subset with 200 essays for lower cost.

all_strategy_array=("error_correction_0113" "overall_enhancement_0113" "overall_simplification_0113" "error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120")

MODEL_LIST=("gpt-3.5-turbo-1106" "gpt-4-1106-preview" "meta-llama/Meta-Llama-3-8B-Instruct" "meta-llama/Meta-Llama-3-70B-Instruct")

dataset_list=("ELLIPSE" "TOEFL11")

openai_url="https://api.openai.com/v1/chat/completions"
openai_key="your-openai-key-here"
deepinfra_url="https://api.deepinfra.com/v1/openai/chat/completions"
deepinfra_api_key="your-deepinfra-key-here"

date="0613"

for dataset_name in "${dataset_list[@]}"
do
    echo "$dataset_name"
    for prompt_method in "zeroshot" "fewshot"
    do
        echo "$prompt_method"
        for model_name in "${MODEL_LIST[@]}"
        do 
            model_short_name=$(echo $model_name | cut -d'/' -f 2)
            echo "$model_short_name"

            # if "gpt" is a substring of model_short_name
            if [[ $model_short_name == *"gpt"* ]]; then
                my_key=$openai_key
                my_url=$openai_url
            elif [[ $model_short_name == *"llama"* ]]; then
                my_key=$deepinfra_api_key
                my_url=$deepinfra_url
            fi

            for strategy in "${all_strategy_array[@]}"
            do 
            
                echo "$strategy"

                request_file="requests/scoring/${dataset_name}/${prompt_method}/${strategy}_${model_short_name}_${date}.jsonl"
                save_file="results/scoring/${dataset_name}/${prompt_method}/${strategy}_${model_short_name}_${date}.jsonl"

                # 检查request_file是否存在
                if [ -f ${request_file} ]; then
                    echo "$request_file 文件存在"
                else
                    echo "$request_file 文件不存在"
                fi
            
                python api_request_parallel_processor_0512.py \
                --requests_filepath "${request_file}" \
                --save_filepath "${save_file}" \
                --request_url "${my_url}" \
                --api_key "${my_key}" \
                --max_requests_per_minute 300 \
                --max_tokens_per_minute 500000 \
                --seconds_to_sleep_each_loop 0.2 \
                --token_encoding_name cl100k_base \
                --max_attempts 5 \
                --logging_level 20
done
done
done
done