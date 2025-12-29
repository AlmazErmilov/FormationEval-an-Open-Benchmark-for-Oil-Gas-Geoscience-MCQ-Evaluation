# FormationEval 0.1 analysis

Last updated: 2025-12-28T13:42:49.053720+00:00

## Hardest questions

Questions failed by the most models:

| Rank | Question ID | Difficulty | Models failed | Correct |
|------|-------------|------------|---------------|---------|
| 1 | formationeval_v0.1_petroleumgeology_strikeslip_stepovers_008 | medium | 61/72 | D |
| 2 | formationeval_v0.1_petrophysics_porosity_lithology_001 | medium | 56/72 | C |
| 3 | formationeval_v0.1_petrophysics_invasion_profile_002 | medium | 55/72 | B |
| 4 | formationeval_v0.1_petrophysics_tool_calibration_002 | medium | 53/72 | D |
| 5 | formationeval_v0.1_petrophysics_cased_hole_limitations_008 | medium | 52/72 | A |
| 6 | formationeval_v0.1_petrophysics_lwd_propagation_005 | easy | 52/72 | D |
| 7 | formationeval_v0.1_petrophysics_pe_log_005 | medium | 50/72 | D |
| 8 | formationeval_v0.1_petrophysics_lithology_id_004 | medium | 47/72 | D |
| 9 | formationeval_v0.1_petrophysics_tool_physics_005 | hard | 47/72 | D |
| 10 | formationeval_v0.1_petrophysics_induction_logging_001 | medium | 45/72 | A |

### Example: Hardest questions

**#1: formationeval_v0.1_petroleumgeology_strikeslip_stepovers_008**

> Consider a right-lateral (dextral) strike-slip fault system with overlapping fault branches. Which arrangement produces extension in the overlap zone, favoring features like pull-apart basins?

- A) Dextral motion with a left-stepping arrangement of segments
- B) Sinistral motion with a left-stepping arrangement of segments
- C) Dextral motion with a planar, unsegmented fault trace
- D) Dextral motion with a right-stepping arrangement of segments **(correct)**

**Model responses:**
- claude-3.5-haiku: A (wrong)
- claude-3.7-sonnet: A (wrong)
- claude-haiku-4.5: A (wrong)
- claude-opus-4.5: A (wrong)
- claude-sonnet-4.5: A (wrong)
- deepseek-r1: A (wrong)
- deepseek-r1-0528-qwen3-8b: A (wrong)
- deepseek-v3.2: A (wrong)
- gemini-2.0-flash-001: A (wrong)
- gemini-2.5-flash: A (wrong)
- gemini-2.5-flash-lite: A (wrong)
- gemini-2.5-pro: A (wrong)
- gemini-3-flash-preview: D (correct)
- gemini-3-pro-preview: D (correct)
- gemma-3-12b-it: A (wrong)
- gemma-3-27b-it: A (wrong)
- gemma-3-4b-it: D (correct)
- gemma-3n-e4b-it: D (correct)
- gpt-4.1: A (wrong)
- gpt-4.1-mini: A (wrong)
- gpt-4.1-nano: A (wrong)
- gpt-4o: A (wrong)
- gpt-4o-mini: A (wrong)
- gpt-5-chat: A (wrong)
- gpt-5-mini-high: A (wrong)
- gpt-5-mini-low: A (wrong)
- gpt-5-mini-medium: A (wrong)
- gpt-5-nano-high: A (wrong)
- gpt-5-nano-low: D (correct)
- gpt-5-nano-medium: D (correct)
- gpt-5.1-chat-high: A (wrong)
- gpt-5.1-chat-low: A (wrong)
- gpt-5.1-chat-medium: A (wrong)
- gpt-5.2-chat-high: A (wrong)
- gpt-5.2-chat-low: A (wrong)
- gpt-5.2-chat-medium: A (wrong)
- llama-3.1-8b-instruct: B (wrong)
- llama-3.2-3b-instruct: C (wrong)
- llama-4-scout: A (wrong)
- phi-4-reasoning-plus: A (wrong)
- minimax-m2: A (wrong)
- ministral-14b-2512: A (wrong)
- ministral-3b-2512: A (wrong)
- ministral-8b-2512: A (wrong)
- mistral-medium-3.1: A (wrong)
- mistral-nemo: D (correct)
- mistral-small-24b-instruct-2501: A (wrong)
- mistral-small-3.2-24b-instruct: A (wrong)
- kimi-k2-thinking: D (correct)
- nemotron-3-nano-30b-a3b: A (wrong)
- nemotron-nano-12b-v2-vl: A (wrong)
- nemotron-nano-9b-v2: A (wrong)
- o3-mini-high: A (wrong)
- o3-mini-low: A (wrong)
- o3-mini-medium: A (wrong)
- o4-mini-high: A (wrong)
- o4-mini-low: A (wrong)
- o4-mini-medium: D (correct)
- gpt-oss-120b: A (wrong)
- gpt-oss-20b: A (wrong)
- qwen3-14b: A (wrong)
- qwen3-235b-a22b-2507: A (wrong)
- qwen3-30b-a3b-thinking-2507: A (wrong)
- qwen3-32b: A (wrong)
- qwen3-8b: A (wrong)
- qwen3-vl-8b-instruct: D (correct)
- qwen3-vl-8b-thinking: A (wrong)
- grok-3-mini: A (wrong)
- grok-4-fast: A (wrong)
- grok-4.1-fast: A (wrong)
- glm-4-32b: A (wrong)
- glm-4.7: D (correct)

**#2: formationeval_v0.1_petrophysics_porosity_lithology_001**

> When using a standard neutron-density crossplot constructed for a limestone matrix to interpret a log where the neutron porosity is recorded in sandstone units, what is the correct procedure for plotting the data points?

- A) Plot the sandstone unit values directly as they appear on the log
- B) Convert the density log to sandstone units before plotting
- C) Use the porosity markings along the sandstone lithology line to guide the horizontal positioning **(correct)**
- D) Subtract the matrix difference (approx. 6 p.u.) from the neutron reading before plotting

**Model responses:**
- claude-3.5-haiku: D (wrong)
- claude-3.7-sonnet: D (wrong)
- claude-haiku-4.5: D (wrong)
- claude-opus-4.5: A (wrong)
- claude-sonnet-4.5: D (wrong)
- deepseek-r1: D (wrong)
- deepseek-r1-0528-qwen3-8b: D (wrong)
- deepseek-v3.2: D (wrong)
- gemini-2.0-flash-001: D (wrong)
- gemini-2.5-flash: D (wrong)
- gemini-2.5-flash-lite: D (wrong)
- gemini-2.5-pro: A (wrong)
- gemini-3-flash-preview: A (wrong)
- gemini-3-pro-preview: C (correct)
- gemma-3-12b-it: D (wrong)
- gemma-3-27b-it: D (wrong)
- gemma-3-4b-it: D (wrong)
- gemma-3n-e4b-it: C (correct)
- gpt-4.1: D (wrong)
- gpt-4.1-mini: D (wrong)
- gpt-4.1-nano: C (correct)
- gpt-4o: D (wrong)
- gpt-4o-mini: D (wrong)
- gpt-5-chat: D (wrong)
- gpt-5-mini-high: D (wrong)
- gpt-5-mini-low: D (wrong)
- gpt-5-mini-medium: D (wrong)
- gpt-5-nano-high: D (wrong)
- gpt-5-nano-low: C (correct)
- gpt-5-nano-medium: D (wrong)
- gpt-5.1-chat-high: C (correct)
- gpt-5.1-chat-low: C (correct)
- gpt-5.1-chat-medium: C (correct)
- gpt-5.2-chat-high: D (wrong)
- gpt-5.2-chat-low: C (correct)
- gpt-5.2-chat-medium: C (correct)
- llama-3.1-8b-instruct: A (wrong)
- llama-3.2-3b-instruct: C (correct)
- llama-4-scout: D (wrong)
- phi-4-reasoning-plus: D (wrong)
- minimax-m2: D (wrong)
- ministral-14b-2512: D (wrong)
- ministral-3b-2512: C (correct)
- ministral-8b-2512: D (wrong)
- mistral-medium-3.1: D (wrong)
- mistral-nemo: D (wrong)
- mistral-small-24b-instruct-2501: D (wrong)
- mistral-small-3.2-24b-instruct: D (wrong)
- kimi-k2-thinking: D (wrong)
- nemotron-3-nano-30b-a3b: C (correct)
- nemotron-nano-12b-v2-vl: D (wrong)
- nemotron-nano-9b-v2: D (wrong)
- o3-mini-high: D (wrong)
- o3-mini-low: D (wrong)
- o3-mini-medium: D (wrong)
- o4-mini-high: D (wrong)
- o4-mini-low: D (wrong)
- o4-mini-medium: D (wrong)
- gpt-oss-120b: C (correct)
- gpt-oss-20b: D (wrong)
- qwen3-14b: D (wrong)
- qwen3-235b-a22b-2507: D (wrong)
- qwen3-30b-a3b-thinking-2507: D (wrong)
- qwen3-32b: D (wrong)
- qwen3-8b: D (wrong)
- qwen3-vl-8b-instruct: D (wrong)
- qwen3-vl-8b-thinking: C (correct)
- grok-3-mini: D (wrong)
- grok-4-fast: D (wrong)
- grok-4.1-fast: D (wrong)
- glm-4-32b: C (correct)
- glm-4.7: C (correct)

**#3: formationeval_v0.1_petrophysics_invasion_profile_002**

> Under what specific condition does a low-resistivity 'annulus' typically form in the transition zone between the flushed zone and the uninvaded formation?

- A) When the drilling mud filtrate is much more resistive than the formation water
- B) When hydrocarbons in the formation are more mobile than the formation water **(correct)**
- C) When the formation is entirely water-bearing and invaded by fresh mud
- D) When gravity segregation separates gas from oil in a horizontal well

**Model responses:**
- claude-3.5-haiku: A (wrong)
- claude-3.7-sonnet: B (correct)
- claude-haiku-4.5: C (wrong)
- claude-opus-4.5: A (wrong)
- claude-sonnet-4.5: B (correct)
- deepseek-r1: B (correct)
- deepseek-r1-0528-qwen3-8b: B (correct)
- deepseek-v3.2: B (correct)
- gemini-2.0-flash-001: A (wrong)
- gemini-2.5-flash: A (wrong)
- gemini-2.5-flash-lite: A (wrong)
- gemini-2.5-pro: A (wrong)
- gemini-3-flash-preview: A (wrong)
- gemini-3-pro-preview: A (wrong)
- gemma-3-12b-it: C (wrong)
- gemma-3-27b-it: C (wrong)
- gemma-3-4b-it: A (wrong)
- gemma-3n-e4b-it: C (wrong)
- gpt-4.1: A (wrong)
- gpt-4.1-mini: B (correct)
- gpt-4.1-nano: C (wrong)
- gpt-4o: A (wrong)
- gpt-4o-mini: A (wrong)
- gpt-5-chat: A (wrong)
- gpt-5-mini-high: A (wrong)
- gpt-5-mini-low: B (correct)
- gpt-5-mini-medium: B (correct)
- gpt-5-nano-high: A (wrong)
- gpt-5-nano-low: C (wrong)
- gpt-5-nano-medium: B (correct)
- gpt-5.1-chat-high: A (wrong)
- gpt-5.1-chat-low: A (wrong)
- gpt-5.1-chat-medium: A (wrong)
- gpt-5.2-chat-high: A (wrong)
- gpt-5.2-chat-low: B (correct)
- gpt-5.2-chat-medium: B (correct)
- llama-3.1-8b-instruct: B (correct)
- llama-3.2-3b-instruct: C (wrong)
- llama-4-scout: C (wrong)
- phi-4-reasoning-plus: A (wrong)
- minimax-m2: A (wrong)
- ministral-14b-2512: C (wrong)
- ministral-3b-2512: A (wrong)
- ministral-8b-2512: C (wrong)
- mistral-medium-3.1: C (wrong)
- mistral-nemo: C (wrong)
- mistral-small-24b-instruct-2501: C (wrong)
- mistral-small-3.2-24b-instruct: C (wrong)
- kimi-k2-thinking: A (wrong)
- nemotron-3-nano-30b-a3b: C (wrong)
- nemotron-nano-12b-v2-vl: C (wrong)
- nemotron-nano-9b-v2: B (correct)
- o3-mini-high: A (wrong)
- o3-mini-low: A (wrong)
- o3-mini-medium: A (wrong)
- o4-mini-high: B (correct)
- o4-mini-low: B (correct)
- o4-mini-medium: B (correct)
- gpt-oss-120b: C (wrong)
- gpt-oss-20b: C (wrong)
- qwen3-14b: A (wrong)
- qwen3-235b-a22b-2507: A (wrong)
- qwen3-30b-a3b-thinking-2507: A (wrong)
- qwen3-32b: A (wrong)
- qwen3-8b: A (wrong)
- qwen3-vl-8b-instruct: A (wrong)
- qwen3-vl-8b-thinking: B (correct)
- grok-3-mini: A (wrong)
- grok-4-fast: C (wrong)
- grok-4.1-fast: A (wrong)
- glm-4-32b: A (wrong)
- glm-4.7: A (wrong)

---

## Model agreement

- All models correct: 109/505 (21.6%)
- All models wrong: 0/505 (0.0%)
- Mixed results: 396/505 (78.4%)

## Bias exploitation analysis

### Position bias (A/B/C/D distribution)

| Model | A | B | C | D | Bias level |
|-------|---|---|---|---|------------|
| claude-3.5-haiku | 33% | 28% | 21% | 18% | Medium |
| claude-3.7-sonnet | 27% | 26% | 26% | 22% | Low |
| claude-haiku-4.5 | 28% | 26% | 27% | 20% | Medium |
| claude-opus-4.5 | 28% | 27% | 24% | 22% | Low |
| claude-sonnet-4.5 | 31% | 26% | 24% | 19% | Medium |
| deepseek-r1 | 26% | 27% | 25% | 23% | Low |
| deepseek-r1-0528-qwen3-8b | 24% | 27% | 26% | 23% | Low |
| deepseek-v3.2 | 27% | 27% | 24% | 22% | Low |
| gemini-2.0-flash-001 | 28% | 26% | 25% | 21% | Low |
| gemini-2.5-flash | 28% | 25% | 25% | 22% | Low |
| gemini-2.5-flash-lite | 29% | 25% | 25% | 21% | Low |
| gemini-2.5-pro | 28% | 25% | 25% | 22% | Low |
| gemini-3-flash-preview | 27% | 26% | 24% | 23% | Low |
| gemini-3-pro-preview | 28% | 26% | 25% | 22% | Low |
| gemma-3-12b-it | 26% | 27% | 26% | 20% | Low |
| gemma-3-27b-it | 27% | 30% | 25% | 18% | Medium |
| gemma-3-4b-it | 27% | 30% | 26% | 17% | Medium |
| gemma-3n-e4b-it | 29% | 28% | 26% | 17% | Medium |
| gpt-4.1 | 28% | 28% | 24% | 20% | Low |
| gpt-4.1-mini | 29% | 27% | 24% | 20% | Low |
| gpt-4.1-nano | 30% | 26% | 25% | 19% | Medium |
| gpt-4o | 27% | 29% | 24% | 20% | Low |
| gpt-4o-mini | 30% | 28% | 25% | 18% | Medium |
| gpt-5-chat | 27% | 27% | 25% | 21% | Low |
| gpt-5-mini-high | 28% | 26% | 25% | 21% | Low |
| gpt-5-mini-low | 27% | 26% | 26% | 22% | Low |
| gpt-5-mini-medium | 28% | 25% | 26% | 22% | Low |
| gpt-5-nano-high | 26% | 26% | 26% | 22% | Low |
| gpt-5-nano-low | 27% | 26% | 25% | 23% | Low |
| gpt-5-nano-medium | 26% | 27% | 26% | 22% | Low |
| gpt-5.1-chat-high | 28% | 28% | 24% | 20% | Low |
| gpt-5.1-chat-low | 29% | 27% | 24% | 21% | Low |
| gpt-5.1-chat-medium | 26% | 27% | 26% | 22% | Low |
| gpt-5.2-chat-high | 27% | 26% | 26% | 22% | Low |
| gpt-5.2-chat-low | 26% | 26% | 26% | 22% | Low |
| gpt-5.2-chat-medium | 27% | 26% | 26% | 22% | Low |
| llama-3.1-8b-instruct | 24% | 30% | 23% | 24% | Low |
| llama-3.2-3b-instruct | 29% | 29% | 26% | 17% | Medium |
| llama-4-scout | 26% | 29% | 25% | 21% | Low |
| phi-4-reasoning-plus | 26% | 27% | 26% | 21% | Low |
| minimax-m2 | 27% | 27% | 25% | 20% | Low |
| ministral-14b-2512 | 28% | 26% | 26% | 20% | Low |
| ministral-3b-2512 | 26% | 34% | 24% | 16% | Medium |
| ministral-8b-2512 | 26% | 30% | 26% | 19% | Medium |
| mistral-medium-3.1 | 27% | 27% | 25% | 22% | Low |
| mistral-nemo | 33% | 28% | 22% | 17% | Medium |
| mistral-small-24b-instruct-2501 | 28% | 25% | 28% | 19% | Medium |
| mistral-small-3.2-24b-instruct | 27% | 27% | 26% | 20% | Medium |
| kimi-k2-thinking | 27% | 26% | 25% | 23% | Low |
| nemotron-3-nano-30b-a3b | 44% | 21% | 20% | 15% | High |
| nemotron-nano-12b-v2-vl | 36% | 24% | 23% | 17% | High |
| nemotron-nano-9b-v2 | 33% | 25% | 23% | 19% | Medium |
| o3-mini-high | 27% | 26% | 26% | 21% | Low |
| o3-mini-low | 27% | 27% | 26% | 21% | Low |
| o3-mini-medium | 26% | 26% | 27% | 21% | Low |
| o4-mini-high | 27% | 26% | 25% | 22% | Low |
| o4-mini-low | 27% | 26% | 26% | 21% | Low |
| o4-mini-medium | 27% | 27% | 25% | 21% | Low |
| gpt-oss-120b | 27% | 26% | 26% | 21% | Low |
| gpt-oss-20b | 27% | 27% | 26% | 21% | Low |
| qwen3-14b | 26% | 26% | 26% | 22% | Low |
| qwen3-235b-a22b-2507 | 29% | 26% | 24% | 21% | Low |
| qwen3-30b-a3b-thinking-2507 | 27% | 26% | 26% | 22% | Low |
| qwen3-32b | 26% | 27% | 25% | 22% | Low |
| qwen3-8b | 26% | 26% | 26% | 22% | Low |
| qwen3-vl-8b-instruct | 27% | 29% | 25% | 20% | Medium |
| qwen3-vl-8b-thinking | 27% | 28% | 25% | 21% | Low |
| grok-3-mini | 27% | 26% | 25% | 21% | Low |
| grok-4-fast | 26% | 27% | 26% | 22% | Low |
| grok-4.1-fast | 27% | 26% | 25% | 22% | Low |
| glm-4-32b | 28% | 28% | 24% | 20% | Low |
| glm-4.7 | 27% | 25% | 25% | 23% | Low |

Expected from uniform distribution: 25% each

### Length bias (picking longest answer)

| Model | % picked longest | vs random (25%) | vs benchmark |
|-------|------------------|-----------------|--------------|
| claude-3.5-haiku | 45% | +20% | -1% |
| claude-3.7-sonnet | 45% | +20% | -2% |
| claude-haiku-4.5 | 47% | +22% | +1% |
| claude-opus-4.5 | 46% | +21% | -0% |
| claude-sonnet-4.5 | 43% | +18% | -3% |
| deepseek-r1 | 46% | +21% | -1% |
| deepseek-r1-0528-qwen3-8b | 43% | +18% | -3% |
| deepseek-v3.2 | 45% | +20% | -1% |
| gemini-2.0-flash-001 | 46% | +21% | -0% |
| gemini-2.5-flash | 45% | +20% | -1% |
| gemini-2.5-flash-lite | 46% | +21% | -0% |
| gemini-2.5-pro | 47% | +22% | +0% |
| gemini-3-flash-preview | 47% | +22% | +0% |
| gemini-3-pro-preview | 47% | +22% | +0% |
| gemma-3-12b-it | 43% | +18% | -3% |
| gemma-3-27b-it | 44% | +19% | -2% |
| gemma-3-4b-it | 40% | +15% | -6% |
| gemma-3n-e4b-it | 39% | +14% | -7% |
| gpt-4.1 | 46% | +21% | +0% |
| gpt-4.1-mini | 47% | +22% | +0% |
| gpt-4.1-nano | 43% | +18% | -3% |
| gpt-4o | 45% | +20% | -1% |
| gpt-4o-mini | 44% | +19% | -2% |
| gpt-5-chat | 45% | +20% | -1% |
| gpt-5-mini-high | 47% | +22% | +0% |
| gpt-5-mini-low | 46% | +21% | -0% |
| gpt-5-mini-medium | 46% | +21% | -0% |
| gpt-5-nano-high | 45% | +20% | -1% |
| gpt-5-nano-low | 45% | +20% | -2% |
| gpt-5-nano-medium | 45% | +20% | -1% |
| gpt-5.1-chat-high | 46% | +21% | -0% |
| gpt-5.1-chat-low | 45% | +20% | -1% |
| gpt-5.1-chat-medium | 46% | +21% | -1% |
| gpt-5.2-chat-high | 46% | +21% | -0% |
| gpt-5.2-chat-low | 46% | +21% | -0% |
| gpt-5.2-chat-medium | 47% | +22% | +0% |
| llama-3.1-8b-instruct | 44% | +19% | -2% |
| llama-3.2-3b-instruct | 38% | +13% | -8% |
| llama-4-scout | 45% | +20% | -1% |
| phi-4-reasoning-plus | 46% | +21% | -0% |
| minimax-m2 | 45% | +20% | -2% |
| ministral-14b-2512 | 43% | +18% | -3% |
| ministral-3b-2512 | 45% | +20% | -1% |
| ministral-8b-2512 | 45% | +20% | -1% |
| mistral-medium-3.1 | 45% | +20% | -1% |
| mistral-nemo | 42% | +17% | -5% |
| mistral-small-24b-instruct-2501 | 46% | +21% | -1% |
| mistral-small-3.2-24b-instruct | 44% | +19% | -2% |
| kimi-k2-thinking | 45% | +20% | -1% |
| nemotron-3-nano-30b-a3b | 39% | +14% | -7% |
| nemotron-nano-12b-v2-vl | 40% | +15% | -5% |
| nemotron-nano-9b-v2 | 43% | +18% | -4% |
| o3-mini-high | 45% | +20% | -1% |
| o3-mini-low | 46% | +21% | -1% |
| o3-mini-medium | 46% | +21% | -0% |
| o4-mini-high | 46% | +21% | -1% |
| o4-mini-low | 45% | +20% | -2% |
| o4-mini-medium | 46% | +21% | -0% |
| gpt-oss-120b | 45% | +20% | -2% |
| gpt-oss-20b | 46% | +21% | -1% |
| qwen3-14b | 46% | +21% | -0% |
| qwen3-235b-a22b-2507 | 47% | +22% | +0% |
| qwen3-30b-a3b-thinking-2507 | 46% | +21% | -1% |
| qwen3-32b | 45% | +20% | -1% |
| qwen3-8b | 46% | +21% | -1% |
| qwen3-vl-8b-instruct | 46% | +21% | -1% |
| qwen3-vl-8b-thinking | 44% | +19% | -2% |
| grok-3-mini | 46% | +21% | +0% |
| grok-4-fast | 46% | +21% | -0% |
| grok-4.1-fast | 47% | +22% | +0% |
| glm-4-32b | 46% | +21% | -1% |
| glm-4.7 | 46% | +21% | -0% |

**Interpretation:**
- **vs random (25%)**: Positive = model prefers longer answers
- **vs benchmark**: Negative = picking longest less often than correct-is-longest rate

## Extraction pattern distribution

How models format their answers:

| Model | answer_colon | answer_is | choice_is | correct_answer | end_of_string | failed | first_char | is_x | letter_paren | letter_period | option | parentheses | standalone |
|-------|------|------|------|------|------|------|------|------|------|------|------|------|------|
| claude-3.5-haiku | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-3.7-sonnet | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-haiku-4.5 | 0% | 0% | 0% | 0% | 4% | 0% | 96% | 0% | 1% | 0% | 0% | 0% | 0% |
| claude-opus-4.5 | 0% | 2% | 0% | 0% | 0% | 0% | 97% | 0% | 0% | 0% | 0% | 0% | 0% |
| claude-sonnet-4.5 | 7% | 4% | 0% | 0% | 7% | 0% | 74% | 0% | 7% | 0% | 1% | 0% | 0% |
| deepseek-r1 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| deepseek-r1-0528-qwen3-8b | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| deepseek-v3.2 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-2.0-flash-001 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-2.5-flash | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-2.5-flash-lite | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-2.5-pro | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-3-flash-preview | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemini-3-pro-preview | 1% | 1% | 0% | 0% | 0% | 0% | 98% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemma-3-12b-it | 0% | 0% | 0% | 0% | 3% | 0% | 97% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemma-3-27b-it | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemma-3-4b-it | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gemma-3n-e4b-it | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4.1 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4.1-mini | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4.1-nano | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4o | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-4o-mini | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-chat | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-mini-high | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-mini-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-mini-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-nano-high | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-nano-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5-nano-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.1-chat-high | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.1-chat-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.1-chat-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.2-chat-high | 0% | 0% | 0% | 0% | 0% | 0% | 99% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.2-chat-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-5.2-chat-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| llama-3.1-8b-instruct | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| llama-3.2-3b-instruct | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| llama-4-scout | 0% | 19% | 0% | 2% | 5% | 0% | 73% | 0% | 0% | 0% | 0% | 0% | 0% |
| phi-4-reasoning-plus | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| minimax-m2 | 5% | 3% | 0% | 0% | 0% | 1% | 90% | 0% | 1% | 0% | 1% | 0% | 0% |
| ministral-14b-2512 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| ministral-3b-2512 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| ministral-8b-2512 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| mistral-medium-3.1 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| mistral-nemo | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| mistral-small-24b-instruct-2501 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| mistral-small-3.2-24b-instruct | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| kimi-k2-thinking | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| nemotron-3-nano-30b-a3b | 0% | 0% | 0% | 0% | 0% | 0% | 98% | 0% | 0% | 0% | 0% | 0% | 1% |
| nemotron-nano-12b-v2-vl | 3% | 6% | 0% | 0% | 1% | 2% | 63% | 0% | 4% | 0% | 10% | 2% | 10% |
| nemotron-nano-9b-v2 | 2% | 6% | 0% | 0% | 0% | 0% | 83% | 0% | 0% | 0% | 9% | 0% | 0% |
| o3-mini-high | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| o3-mini-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| o3-mini-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| o4-mini-high | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| o4-mini-low | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| o4-mini-medium | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| gpt-oss-120b | 0% | 0% | 0% | 0% | 20% | 0% | 78% | 0% | 0% | 1% | 1% | 0% | 0% |
| gpt-oss-20b | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-14b | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-235b-a22b-2507 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-30b-a3b-thinking-2507 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-32b | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-8b | 0% | 0% | 0% | 0% | 0% | 2% | 98% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-vl-8b-instruct | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| qwen3-vl-8b-thinking | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-3-mini | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-4-fast | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| grok-4.1-fast | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| glm-4-32b | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
| glm-4.7 | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 0% | 0% | 0% | 0% | 0% | 0% |
