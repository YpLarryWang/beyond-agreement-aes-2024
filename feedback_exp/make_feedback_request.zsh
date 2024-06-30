#!/bin/zsh

dataset_name="ELLIPSE"
prompt_method="fewshot"
model_name="gpt-4-1106-preview"

all_strategy_array=("error_correction_0113" "overall_enhancement_0113" "overall_simplification_0113" "error_introduction_paragraph_0120" "error_introduction_discourse_0120" "error_introduction_in_sentence_spelling_0120" "error_introduction_in_sentence_word_order_0120" "error_introduction_in_sentence_sva_0120")

date="0127"

for strategy in "${all_strategy_array[@]}"
do
    python feedback_exp/make-aes-ell-fewshot-multiturn-feedback-requests.py \
    --feedback-instruct prompts/feedback/feedback-multi-turn.txt \
    --last-turn-file results/scoring/${dataset_name}/${prompt_method}/subset200_${strategy}_${model_name}_${date}.jsonl \
    --output-file requests/feedback/ELLIPSE/fewshot/subset200_${strategy}_${model_name}_${date}.jsonl
done

python feedback_exp/select_subset25_feedback_request.py