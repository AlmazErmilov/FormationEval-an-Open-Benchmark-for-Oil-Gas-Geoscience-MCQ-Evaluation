#!/usr/bin/env python3
"""Export per-question model answers from questions.csv to JSON for website quiz feature."""

import pandas as pd
import json

df = pd.read_csv('eval/results/questions.csv')

# CSV columns follow pattern: {model}_answer, {model}_correct, {model}_pattern, {model}_raw
# We only need: question_id, {model}_answer, {model}_correct

model_answers = {}
for _, row in df.iterrows():
    qid = row['question_id']
    model_answers[qid] = {}

    # Find all model columns (those ending in _answer)
    for col in df.columns:
        if col.endswith('_answer') and col != 'correct_answer':
            model_id = col.replace('_answer', '')
            correct_val = row[f'{model_id}_correct']
            model_answers[qid][model_id] = {
                'answer': str(row[col]) if pd.notna(row[col]) else None,
                'correct': bool(correct_val) if isinstance(correct_val, bool) else str(correct_val).lower() == 'true'
            }

with open('../formationeval-website/src/data/model-answers.json', 'w') as f:
    json.dump(model_answers, f)

print(f"Exported {len(model_answers)} questions, {len(model_answers[list(model_answers.keys())[0]])} models")
