#!/bin/zsh

# model finetuning is done on openai platform
# so in this script, we only show how to make requests for scoring with finetuned models

today=$(date "+%m%d")

rule_based_intervention_strategy_array=("error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120")

gpt4_intervention_strategy_array=("error_correction_0113" "overall_enhancement_0113" "overall_simplification_0113")

dataset_list=("ELLIPSE" "TOEFL11")

for dataset_name in "${dataset_list[@]}"
do
    echo "Processing $dataset_name"

    if [ $dataset_name = "TOEFL11" ]; then
        typeset -A train_size_to_model_id=(
            [50]="ft:gpt-3.5-turbo-1106:personal::8qAxJmf8"
            [100]="ft:gpt-3.5-turbo-1106:personal::8nKoqXJE"
            [200]="ft:gpt-3.5-turbo-1106:personal::8q4eINfJ"
            [400]="ft:gpt-3.5-turbo-1106:personal::8q4XZyHX"
            [800]="ft:gpt-3.5-turbo-1106:personal::8rVWHAlI"
        )
    elif [ $dataset_name = "ELLIPSE" ]; then
        typeset -A train_size_to_model_id=(
            [50]="ft:gpt-3.5-turbo-1106:personal::8qAwaiCQ"
            [100]="ft:gpt-3.5-turbo-1106:personal::8nKmnphk"
            [200]="ft:gpt-3.5-turbo-1106:personal::8q4GrpCH"
            [400]="ft:gpt-3.5-turbo-1106:personal::8q4h5b1d"
            [800]="ft:gpt-3.5-turbo-1106:personal::8rVYtKDC"
        )
    fi

    for train_size in "${(@k)train_size_to_model_id}"
    do
        model_name=${train_size_to_model_id[$train_size]}
        echo "Processing $model_name"

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
            --output-file requests/scoring/${dataset_name}/finetune/original_ft${train_size}_${today}.jsonl \
            --dataset ${dataset_name} \
            --fine-tune

        for strategy in "${rule_based_intervention_strategy_array[@]}"
        do
            echo "Processing $strategy"

            python scoring_exp/make-aes-cfact-zeroshot-request.py \
                --essay-dir data/${dataset_name}/cfact/rule-based/${strategy}_counterfactuals.jsonl \
                --id-field ${ID_FIELD} \
                --text-field text \
                --prompt-dir prompts/scoring/${dataset_name} \
                --model-id "${model_name}" \
                --output-file requests/scoring/${dataset_name}/finetune/${strategy}_ft${train_size}_${today}.jsonl \
                --dataset ${dataset_name} \
                --fine-tune
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
                --output-file requests/scoring/${dataset_name}/finetune/${strategy}_ft${train_size}_${today}.jsonl \
                --dataset ${dataset_name} \
                --fine-tune
        done
    done
done