#!/bin/zsh

python cf_gen_0610/make_cf_gen_request.py \
  --model_id meta-llama/Meta-Llama-3-70B-Instruct \
  --sys_msg_file data_submission_0215/prompts_0213/system/cf_gen_background_1219.txt \
  --user_msg_file data_submission_0215/prompts_0213/cf_gen/overall_simplification_1220.txt \
  --input_file results/cf_gen_202406/TOEFL11/CLEAN_results_TOEFL11_Meta-Llama-3-70B-Instruct-0611_error_correction_deepinfra.jsonl \
  --output_dir requests/cf_gen_202406/TOEFL11/ \
  --id_field file_id \
  --text_field output_essay \
  --request_style deepinfra \
  --transformation overall_simplification \
  --dataset TOEFL11

# python cf_gen_0610/make_cf_gen_request.py \
#   --model_id llama3-70b-8192 \
#   --sys_msg_file data_submission_0215/prompts_0213/system/cf_gen_background_1219.txt \
#   --user_msg_file data_submission_0215/prompts_0213/cf_gen/error_correction_intruction_0610.txt \
#   --input_file data_submission_0215/TOEFL11/test.jsonl \
#   --output_dir requests/cf_gen_202406/TOEFL11/ \
#   --id_field file_id \
#   --text_field text \
#   --request_style groq \
#   --transformation error_correction \
#   --dataset TOEFL11