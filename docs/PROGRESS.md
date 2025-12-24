# Progress log

## 2025-12-24: System prompt updates to prevent bias at generation time

### Problem

Analysis of the few-shot examples in `src/prompts/mcq_generator_system_prompt.txt` revealed they contradicted the text guidance:
- 2 of 3 examples had correct answer as the longest option
- No examples demonstrated qualifier word balance
- Text said "avoid patterns where correct answer is always longest" but examples showed the opposite

LLMs learn more from examples than from text instructions, so the examples were teaching the wrong behavior.

### Changes made

**1. Added qualifier word guidance section** (after Balance section)

New guidance about using absolute words ("always", "never") and hedged words ("may", "can") in both correct answers and distractors to prevent exploitable patterns.

**2. Updated note before examples**

Added reminder that examples demonstrate length balance.

**3. Added 2 items to `<what_not_to_do>` section**

Explicit prohibitions against:
- Making correct answer consistently longest/shortest
- Creating exploitable word patterns (absolute words only in distractors, hedged words only in correct answers)

**4. Fixed all three few-shot examples for length balance**

| Example | Correct | Before (chars) | After (chars) | Result |
|---------|---------|----------------|---------------|--------|
| 1 | B | A:66, B:48, C:66, D:48 | A:66, B:61, C:66, D:63 | B no longer shortest |
| 2 | D | A:62, B:56, C:42, D:72 | A:71, B:68, C:66, D:72 | D no longer clearly longest |
| 3 | C | A:57, B:55, C:66, D:58 | A:69, B:64, C:66, D:67 | C no longer longest (A is) |

### Rationale

Fixing bias at generation time is more efficient than post-generation cleanup. The dataset required 136 edits to fix length and qualifier biases. Updated examples should reduce this burden for future question generation.

---

## 2025-12-23: Bias analysis and fix planning

### Completed
1. **LaTeX → UTF-8 conversion**: All 45 LaTeX patterns across 21 questions converted to Unicode
2. **Known limitations documented** in `data/benchmark/README.md`
3. **Deep bias analysis** - full report below

---

## Detailed bias analysis report

### Issue #1: Answer length bias

**Criticality: HIGH (8/10)**

| Position | Count | Actual | Expected | Deviation |
|----------|-------|--------|----------|-----------|
| Longest (correct) | 326 | 64.6% | 25% | +39.6% |
| 2nd longest | 81 | 16.0% | 25% | -9.0% |
| 3rd longest | 55 | 10.9% | 25% | -14.1% |
| Shortest | 43 | 8.5% | 25% | -16.5% |

**By difficulty (critical finding)**:
| Difficulty | Longest=correct | Assessment |
|------------|-----------------|------------|
| Easy | 50.8% | Acceptable |
| Medium | 63.9% | Concerning |
| Hard | **84.8%** | Severe |

**Character counts**:
- Correct answer avg: 86.6 chars
- Distractor avg: 69.8 chars
- Difference: +16.7 chars

### Issue #2: Qualifier word bias

**Criticality: CRITICAL (9/10)**

**Absolute words (almost never correct)**:
| Word | In correct | In distractor | Correct rate |
|------|------------|---------------|--------------|
| always | 0 | 49 | 0.0% |
| never | 0 | 3 | 0.0% |
| only | 3 | 108 | 2.7% |
| all | 3 | 33 | 8.3% |
| completely | 0 | 7 | 0.0% |
| entirely | 0 | 5 | 0.0% |
| impossible | 0 | 5 | 0.0% |

**Hedged words (almost always correct)**:
| Word | In correct | In distractor | Correct rate |
|------|------------|---------------|--------------|
| may | 13 | 0 | 100.0% |
| can | 50 | 16 | 75.8% |
| often | 10 | 2 | 83.3% |
| tends to | 15 | 6 | 71.4% |

**162 questions (32%) contain exploitable patterns.**

### Issue #3: Structural patterns

**Criticality: MODERATE (4/10)**

| Pattern | In correct | In distractor | Diff |
|---------|------------|---------------|------|
| Contains comma | 38.6% | 27.8% | +10.8% |
| Contains parentheses | 10.7% | 3.4% | +7.3% |
| Contains "while" | 6.3% | 3.4% | +3.0% |

### Issue #4: Position distribution

**Criticality: LOW (2/10)**

| Position | Count | Percentage |
|----------|-------|------------|
| A | 138 | 27.3% |
| B | 130 | 25.7% |
| C | 124 | 24.6% |
| D | 113 | 22.4% |

Well balanced - not a concern.

---

## Combined impact

**A model could achieve ~70% accuracy using ONLY surface heuristics:**
- Random baseline: 25%
- Pick longest: 64.6%
- Exploit qualifiers: +5-10%
- Combined: ~68-72%

**Comparison to standards**:
| Benchmark | Length bias | Qualifier bias |
|-----------|-------------|----------------|
| MMLU | ~35-40% | Mild |
| ARC | ~30-35% | Moderate |
| FormationEval v0.1 | **64.6%** | **Severe** |

---

## Fix strategies

### Phase 1: Low risk (immediate)
- Remove "always" from 13 safe instances
- Expand 17 very short distractors
- Expected: 64.6% → ~58-60%

### Phase 2: Expert review
- Review 36 "always" cases
- Review 108 "only" cases
- Add hedged words to distractors
- Expected: ~58% → ~48-52%

### Phase 3: Deep fixes
- Regenerate 84 hard questions
- Expand remaining short distractors
- Expected: ~50% → ~35-40%

---

## 2025-12-23: Length bias fixes applied

### Strategy: EXPAND, don't delete

Added technical context to distractors to match/exceed correct answer length while preserving factual incorrectness.

### Fixes applied

| Category | Fixed | Total |
|----------|-------|-------|
| "always" distractor expansions | 49 | 49 |
| "only" distractor expansions | 87 | 89 |

### Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Longest=correct | 64.6% | 51.5% | **-13.1pp** |
| Distractor avg length | 69.8 chars | 74.0 chars | +4.2 chars |
| Length gap | +16.7 chars | +12.6 chars | **-4.1 chars** |

### Position distribution after fixes

| Position | Before | After |
|----------|--------|-------|
| Longest (correct) | 64.6% | 45.7% |
| 2nd longest | 16.0% | 29.7% |
| 3rd longest | 10.9% | 13.9% |
| Shortest | 8.5% | 10.7% |

### Remaining work

Qualifier word bias still present (not addressed in this round):
- "always" → 0% correct rate (exploitable)
- "may" → 100% correct rate (exploitable)

See `docs/bias_fix_tracking.md` for full details.

---

## 2025-12-23: "Always" vocabulary diversification

### Strategy: Substitute with varied synonyms

Replaced all 49 instances of "always" in distractors with context-appropriate synonyms to break the single-word exploit pattern.

### Substitution rules

1. **Context-aware selection**: Match word to semantic context
   - Comparatives (greater/higher) → invariably, necessarily
   - Change verbs (increases/decreases) → consistently, necessarily
   - Causation (causes/prevents) → inherently, intrinsically
   - Properties (contains/has) → universally, invariably

2. **Avoid redundancy**: Skip words already in the sentence
   - "always fundamentally" → "invariably fundamentally" (not "inherently fundamentally")

3. **Natural flow**: Ensure grammatical naturalness
   - "must always be" → "must necessarily be"

### Distribution of replacements

| Word | Count | % |
|------|-------|---|
| invariably | 12 | 24% |
| necessarily | 12 | 24% |
| inherently | 11 | 22% |
| consistently | 8 | 16% |
| intrinsically | 5 | 10% |
| universally | 1 | 2% |

### Results

| Metric | Before | After |
|--------|--------|-------|
| "always" in distractors | 49 | 0 |
| Simple heuristic "always=wrong" | Works (100%) | Broken |
| Vocabulary diversity | 1 word | 6 words |

### Partial success

- ✓ Broke single-word "always" exploit pattern
- ✓ Diversified absolute vocabulary across 6 words
- ✓ Each new word appears in only 8-12 distractors (vs 49)
- ✗ Combined "any-absolute-word=wrong" pattern still exploitable
- ✗ All 6 new words have 0% in correct answers

### Next steps for full fix

To fully address qualifier bias:
1. Add "invariably/necessarily/inherently" to ~10-15 correct answers where scientifically accurate
2. Add "may/can" to ~10-15 distractors where claim remains wrong
3. This requires domain expertise to verify scientific accuracy

---

## 2025-12-23: "May" distractor additions

### Strategy: Add "may" to distractors with "no-effect" claims

Added "may" to 13 distractors that claim something "has no effect" or "is independent of" when that's factually wrong. These remain wrong because they still assert no relationship exists.

### Selection criteria

Safe patterns for "may" addition:
- "X has no effect on Y" → "X may have no effect on Y" (still claims no effect)
- "X is independent of Y" → "X may be independent of Y" (still claims no relationship)
- "X cannot affect Y" → "X may not affect Y" (still denies effect)

### Modifications applied

| ID | Position | Pattern modified |
|----|----------|------------------|
| petrophysics_clay_conductivity_004 | D | "is independent of" |
| petrophysics_dielectric_salinity_003 | B | "has no effect" |
| petrophysics_gamma_interactions_003 | B | "is independent of" |
| petrophysics_salinity_effect_006 | D | "has no effect" |
| petrophysics_pulsed_neutron_physics_002 | D | "are independent of" |
| petrophysics_nmr_diffusion_003 | B | "has no effect" |
| petrophysics_fluid_properties_006 | B | "is independent of" |
| petrophysics_wave_propagation_004 | D | "is independent of" |
| petrophysics_porosity_evaluation_008 | A | "is independent of" |
| petrophysics_permeability_stoneley_008 | B | "has no effect" |
| petrophysics_volumetric_pe_012 | B | "is independent of" |
| reservoirengineering_overpressure_compaction_011 | D | "has no influence" |
| geophysics_rock_physics_link_001 | D | "cannot affect" |

### Results

| Metric | Before | After |
|--------|--------|-------|
| "may" in correct answers | 13 | 13 |
| "may" in distractors | 0 | 13 |
| "may" correct rate | 100% | **50%** |

### Success

- ✓ Broke "may = correct" exploit pattern completely
- ✓ All modified distractors remain factually wrong
- ✓ No domain expertise required (used "no-effect" patterns only)

### Remaining qualifier bias issues

| Word | In correct | In distractor | Correct rate | Status |
|------|------------|---------------|--------------|--------|
| may | 13 | 13 | 50% | ✓ Fixed |
| never | 0 | 3 | 0% | Not addressed |
| only | 3 | 108 | 2.7% | Not addressed |
| invariably | 0 | 12 | 0% | Still exploitable |
| necessarily | 0 | 12 | 0% | Still exploitable |
| inherently | 0 | 11 | 0% | Still exploitable |
