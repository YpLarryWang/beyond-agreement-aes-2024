#!/bin/zsh

dataset_list=("ELLIPSE")
model_list=("gpt-4-1106-preview")

intervention_strategy_array=("error_correction_0113" "error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120" "overall_enhancement_0113" "overall_simplification_0113")

openai_url="https://api.openai.com/v1/chat/completions"
my_key="your-openai-key-here"

date="0127"
prompt_method="fewshot"

for dataset in "${dataset_list[@]}"
do
    echo "Processing $dataset"
    for model_name in "${model_list[@]}"
    do
        echo "Processing $model_name"
        for strategy in "${intervention_strategy_array[@]}"
        do
            echo "Processing $strategy"

            request_file="requests/feedback/${dataset}/${prompt_method}/subset25_${strategy}_${model_name}_${date}.jsonl"
            save_file="results/feedback/${dataset}/${prompt_method}/subset25_${strategy}_${model_name}_${date}.jsonl"

            if [ ! -e "$request_file" ]; then
                echo "$request_file does not exist."
            else
                echo "$request_file exists."
            fi

            python api_request_parallel_processor.py \
            --requests_filepath "${request_file}" \
            --save_filepath "${save_file}" \
            --request_url "${openai_url}" \
            --api_key "${my_key}" \
            --max_requests_per_minute 300 \
            --max_tokens_per_minute 300000 \
            --token_encoding_name cl100k_base \
            --max_attempts 5 \
            --logging_level 20

            echo "Done"
        done
    done
done