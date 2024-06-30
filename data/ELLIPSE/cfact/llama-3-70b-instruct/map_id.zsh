#!/bin/zsh

python data_submission_0615/ELLIPSE/cfact/llama-3-70b-instruct/map_id.py \
    --jsonl_path data_submission_0615/ELLIPSE/cfact/llama-3-70b-instruct/overall_simplification_0611_counterfactuals.jsonl \
    --mapping_path data_submission_0615/ELLIPSE/id_mapping.json \
    --output_path data_submission_0615/ELLIPSE/cfact/llama-3-70b-instruct/overall_simplification_0611_counterfactuals_mapped.jsonl