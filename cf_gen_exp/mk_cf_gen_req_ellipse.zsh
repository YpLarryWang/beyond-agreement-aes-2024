#!/bin/zsh

DATASET_LIST=(
  "TOEFL" "ELLIPSE"
)
MODEL_LIST=(
  "gpt-4-1106-preview" "meta-llama/Meta-Llama-3-70B-Instruct"
)
INTERVENTION_LIST=(
  "error_correction" "overall_enhancement" "overall_simplification"
)

for dataset in $DATASET_LIST; do
    if [[ $dataset == "TOEFL" ]]; then
        id_field="id"
for model_name in $MODEL_LIST; do
    for intervention in $INTERVENTION_LIST; do

        if [[ $model_name == *"gpt"* ]]; then
            request_style="openai"
        elif [[ $model_name == *"meta"* ]]; then
            request_style="deepinfra"
        fi

        python cf_gen_exp/make_cf_gen_request.py \
        --model_id $model_name \
        --sys_msg_file prompts/system/cf_gen_system.txt \
        --user_msg_file prompts/cf_gen/${intervention}_user_msg_template.txt \
        --input_file data/ELLIPSE/test.jsonl \
        --output_dir requests/cf_gen/ELLIPSE/ \
        --id_field text_id \
        --text_field full_text \
        --request_style ${request_style} \
        --transformation ${intervention} \
        --dataset ELLIPSE
    
    done
done
