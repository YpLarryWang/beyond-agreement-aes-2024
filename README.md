Codes and data for the paper *"Beyond Agreement: Diagnosing the Rationale Alignment of Automated Essay Scoring Methods based on Linguistically-informed Counterfactuals"*.

This repo contains:
1. the prompts used to instruct LLMs, including the prompts used to generate the counterfactual samples in directory `prompts/`, the prompts used to score the essays and the prompts used to generate feedback. Specifically:
   - `system`: system messages
   - `cf_gen`: user messages used to generate counterfactual samples
   - `scoring`: user messages used to score the essays (both the original and the counterfactual samples)
   - `feedback`: user messages used to generate feedback
2. the test set essays and corresponding counterfactual essays for both the TOEFL11 and ELLIPSE datasets in directory `data/`, specifically, counterfactual samples are stored in sub-directory `data/${DATASET_NAME}/cfact`.
3. few-shot examples for both the TOEFL11 and ELLIPSE datasets in directory `data/`. Both files are called `medoids_dict.json`
4. Python and shell scripts to control the whole experimental process:
   1. for detail of counterfactual generation, please refer to sub-directory `cf_gen_exp/`;
   2. for detail of scoring, please refer to sub-directory `scoring_exp/`;
   3. for detail of feedback generation, please refer to sub-directory `feedback_exp/`.