#!/bin/zsh

# In practice, gpt series can return well-formatted json output while for llama series, filting is needed
# In our case, we choose gpt-3.5-turbo-1106 as filter to extract the output score

openai_url="https://api.openai.com/v1/chat/completions"
openai_key="your-openai-key-here"

intervention_strategy_array=("original" "error_correction_0113" "error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120" "overall_enhancement_0113" "overall_simplification_0113")

MODEL_LIST=("gpt-3.5-turbo-1106" "gpt-4-1106-preview" "meta-llama/Meta-Llama-3-8B-Instruct" "meta-llama/Meta-Llama-3-70B-Instruct")

DATASET_LIST=("ELLIPSE" "TOEFL11")

date="0613"

for dataset_name in "${DATASET_LIST[@]}"
do
    echo "Processing $dataset_name"
    
    for prompt_method in "zeroshot" "fewshot"
    do
        echo "Processing $prompt_method"
        for model_name in "${MODEL_LIST[@]}"
        do
            model_short_name=$(echo $model_name | cut -d'/' -f 2)
            echo "Processing $model_short_name"

            for strategy in ${intervention_strategy_array[@]}
            do
                python scoring_exp/parse_aes_results.py \
                --request_file requests/scoring/${dataset_name}/${prompt_method}/${strategy}_${model_short_name}_${date}.jsonl \
                --api_output results/scoring/${dataset_name}/${prompt_method}/${strategy}_${model_short_name}_${date}.jsonl \
                --score_field "score" \

                request_file=results/scoring/${dataset_name}/${prompt_method}/ERROR_${strategy}_${model_short_name}_${date}.jsonl
                save_file="results/scoring/${dataset_name}/${prompt_method}/DONE_ERROR_${strategy}_${model_short_name}_${date}.jsonl"

                if test -f ${request_file}; then
                    echo "File ${request_file} exists."
                else
                    echo "File ${request_file} does not exist."
                fi

                if [ -s "${request_file}" ]; then
                    python api_request_parallel_processor_0512.py \
                        --requests_filepath "${request_file}" \
                        --save_filepath "${save_file}" \
                        --request_url "${openai_url}" \
                        --api_key "${openai_key}" \
                        --max_requests_per_minute 300 \
                        --max_tokens_per_minute 300000 \
                        --seconds_to_sleep_each_loop 0.001 \
                        --token_encoding_name cl100k_base \
                        --max_attempts 5 \
                        --logging_level 20

                    python scoring_exp/parse_and_merge_scoring_filter_results.py \
                        --orig_result results/scoring/${dataset_name}/${prompt_method}/SUCCESS_${strategy}_${model_short_name}_${date}.jsonl \
                        --api_output results/scoring/${dataset_name}/${prompt_method}/DONE_ERROR_${strategy}_${model_short_name}_${date}.jsonl \
                        --id_field text_id

                else
                    # dir of the original file
                    original_file="results/scoring/${dataset_name}/${prompt_method}/SUCCESS_${strategy}_${model_short_name}_${date}.jsonl"

                    # get the directory of the file
                    dir=$(dirname "$original_file")

                    # get the base name of the file
                    base_name=$(basename "$original_file")

                    # add prefix
                    new_file="${dir}/CLEANED_${base_name}"

                    # copy the file
                    cp "$original_file" "$new_file"

                    echo "${request_file} is empty, copied to ${new_file}"
                fi
            done
        done
    done
done