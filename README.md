Codes and data for the paper *"Beyond Agreement: Diagnosing the Rationale Alignment of Automated Essay Scoring Methods based on Linguistically-informed Counterfactuals"*.

This repo contains:
1. the prompts used to instruct LLMs, including the prompts used to generate the counterfactual samples, the prompts used to score the essays and the prompts used to generate feedback. Specifically:
   - `system`: system messages
   - `cf_gen`: user messages used to generate counterfactual samples
   - `scoring`: user messages used to score the essays (both the original and the counterfactual samples)
   - `feedback`: user messages used to generate feedback
2. the test sets and corresponding counterfactual samples for both the TOEFL11 and ELLIPSE datasets.