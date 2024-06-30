#!/bin/zsh

python cf_gen_exp/error_introduction.py \
--input-file data/ELLIPSE/test.jsonl \
--output-dir data/ELLIPSE/cfact/rule-based \
--id-col "text_id" \
--text-col "full_text" \
--no-debug

python cf_gen_exp/error_introduction.py \
--input-file data/TOEFL11/test.jsonl \
--output-dir data/TOEFL11/cfact/rule-based \
--id-col "file_id" \
--text-col "text" \
--no-debug