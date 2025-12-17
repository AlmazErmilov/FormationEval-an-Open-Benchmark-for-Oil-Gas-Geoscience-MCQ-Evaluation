# MCQ generation pipeline

Scripts for generating concept-based multiple-choice questions from source materials.

---

## Files

| File | Purpose |
|------|---------|
| `generate_mcq.py` | Main script to generate MCQs from chapter text |
| `prompts/mcq_generator_system_prompt.txt` | System prompt example (actually draft v1 for now) for the LLM |

---

## Quick start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. Run generation:
   ```bash
   python src/generate_mcq.py chapter.txt 15
   ```
   This generates 15 MCQs from `chapter.txt` and saves to `chapter_mcqs.jsonl`.

---

## Concept-based approach

We generate questions by extracting **concepts** from source material, then writing **original questions** that test understanding of those concepts.

> Full guidelines are in the system prompt (example, draft v1): [`prompts/mcq_generator_system_prompt.txt`](prompts/mcq_generator_system_prompt.txt)

### Why this is safe-ish (see note below)

Copyright protects **expression** (specific wording), not **ideas or facts**.

| What we do | Why it's OK |
|------------|-------------|
| Read and understand concepts | Learning is not infringement |
| Write new questions in our own words | Original expression |
| Use technical terms (e.g., "porosity") | Facts and terminology are not copyrightable |

| What we avoid | Why it's risky |
|---------------|----------------|
| Copying sentences from source | Direct copying of expression |
| Minimal word substitutions | Close paraphrase = derivative work |
| Reproducing distinctive problem structures | Copying unique expression |

### Safeguards in the System Prompt

The LLM is instructed to:
- Extract the underlying concept first
- Write fresh questions and answers in its own words
- Never copy or lightly edit source text
- Use technical terms as-is, but make explanations original

All generated items are tagged `derivation_mode: concept_based` to document this approach.

> **The "-ish":** this safety depends on the LLM following instructions properly. Modern models (GPT-4+, Claude 3+) are quite reliable at instruction following, but **human spot checking remains important** to catch edge cases.

---

## Output format

Questions are saved as JSONL with this structure:

```json
{
  "question": "...",
  "choices": ["A", "B", "C", "D"],
  "answer_index": 0,
  "answer_key": "A",
  "rationale": "...",
  "difficulty": "medium",
  "topics": ["Topic1", "Topic2"],
  "domains": ["Petrophysics"]
}
```

See main README.md for full schema.
