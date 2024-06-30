#!/bin/zsh

today=$(date "+%m%d")

rule_based_intervention_strategy_array=("error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120")

gpt4_intervention_strategy_array=("error_correction_0113" "overall_enhancement_0113" "overall_simplification_0113")

MODEL_LIST=("gpt-3.5-turbo-1106" "gpt-4-1106-preview" "meta-llama/Meta-Llama-3-8B-Instruct" "meta-llama/Meta-Llama-3-70B-Instruct")

dataset_list=("ELLIPSE" "TOEFL11")

for dataset_name in "${dataset_list[@]}"
do
    echo "Processing $dataset_name"
    for model_name in "${MODEL_LIST[@]}"
    do
        model_short_name=$(echo $model_name | cut -d'/' -f 2)
        echo "Processing $model_short_name"

        ############################
        # process original test set essays first
        ############################

        if [ $dataset_name = "TOEFL11" ]; then
            ID_FIELD="file_id"
            TEXT_FIELD="text"
        elif [ $dataset_name = "ELLIPSE" ]; then
            ID_FIELD="text_id"
            TEXT_FIELD="full_text"
        fi

        python scoring_exp/make-aes-cfact-zeroshot-request.py \
            --essay-dir data/${dataset_name}/test.jsonl \
            --id-field ${ID_FIELD} \
            --text-field ${TEXT_FIELD} \
            --prompt-dir prompts/scoring/${dataset_name} \
            --model-id "${model_name}" \
            --output-file requests/scoring/${dataset_name}/zeroshot/original_${model_short_name}_${today}.jsonl \
            --dataset ${dataset_name}

        for strategy in "${rule_based_intervention_strategy_array[@]}"
        do
            echo "Processing $strategy"

            python scoring_exp/make-aes-cfact-zeroshot-request.py \
                --essay-dir data/${dataset_name}/cfact/rule-based/${strategy}_counterfactuals.jsonl \
                --id-field ${ID_FIELD} \
                --text-field text \
                --prompt-dir prompts/scoring/${dataset_name} \
                --model-id "${model_name}" \
                --output-file requests/scoring/${dataset_name}/zeroshot/${strategy}_${model_short_name}_${today}.jsonl \
                --dataset ${dataset_name}
        done

        for strategy in "${gpt4_intervention_strategy_array[@]}"
        do
            echo "Processing $strategy"

            python scoring_exp/make-aes-cfact-zeroshot-request.py \
                --essay-dir data/${dataset_name}/cfact/gpt-4-1106-preview/${strategy}_counterfactuals.jsonl \
                --id-field ${ID_FIELD} \
                --text-field output_essay \
                --prompt-dir prompts/scoring/${dataset_name} \
                --model-id "${model_name}" \
                --output-file requests/scoring/${dataset_name}/zeroshot/${strategy}_${model_short_name}_${today}.jsonl \
                --dataset ${dataset_name}
        done
    done
done