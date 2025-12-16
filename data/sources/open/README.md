# Open-Licensed Sources

Registry of open-licensed materials for public MCQ generation. Actual PDFs/materials go in this folder alongside this README.

---

## Source Catalog

| Domain | Resource | License | Risk | Good for | Link | Local |
|--------|----------|---------|------|----------|------|-------|
| Reservoir Engineering | **Petroleum Reservoir Dynamics** (Zeidouni, LSU) | CC BY-NC 4.0 | NC only | Darcy flow, transient analysis, well tests. Includes chapter quizzes. | [LSU Repository](https://repository.lsu.edu/etext/4/) | `Petroleum Reservoir Dynamics.pdf` |
| PVT / Thermodynamics | **Phase Relations in Reservoir Engineering** (Adewumi, Penn State) | CC BY-NC-SA 4.0 | NC only | Phase behavior, EOS, phase diagrams, VLE calculations. | [LibreTexts](https://eng.libretexts.org/Bookshelves/Chemical_Engineering/Phase_Relations_in_Reservoir_Engineering_(Adewumi)) | — |
| Petrophysics | **Borehole Geophysics Applied to Ground-Water Investigations** (Keys, USGS) | Public Domain | Unrestricted | Tool physics: GR, Neutron, Density, Sonic, Resistivity. Log interpretation. | [USGS TWRI 2-E2](https://pubs.usgs.gov/twri/twri2-e2/) | `TWRI_2-E2.pdf` |
| Petroleum Geology | **Petroleum Geology** (TU Delft OCW) | CC BY-NC-SA 4.0 | NC only | Petroleum systems, basin analysis, exploration workflow. Course content only — references copyrighted textbooks. | [TU Delft OCW](https://ocw.tudelft.nl/courses/petroleum-geology/) | `Petroleum Geology - TU Delft OCW/` |
| Sedimentology | **Sedimentary Geology: Rocks, Environments and Stratigraphy** (Rygel & Quinton, SUNY) | CC BY-SA 4.0 | Unrestricted | Visual interpretation, sedimentary structures, facies analysis. Image-rich. | [LibreTexts](https://geo.libretexts.org/Courses/SUNY_Potsdam/Sedimentary_Geology%3A_Rocks_Environments_and_Stratigraphy) | `SEDIMENTARY GEOLOGY - ROCKS, ENVIRONMENTS AND STRATIGRAPHY.pdf` |

---

## Risk Levels Explained

| Risk | Meaning |
|------|---------|
| **Unrestricted** | Public Domain or CC BY/BY-SA. No restrictions on derivatives or commercial use. Safest for any benchmark use. |
| **NC only** | CC BY-NC or BY-NC-SA. Derivatives allowed for **non-commercial use only**. Fine for research/academic benchmarks. |
| **Verify** | Open Access or Open Courseware without explicit CC license. Check specific terms before large-scale use. |

---

## Excluded Resources (Copyrighted)

These are authoritative industry standards but **cannot be used** for the open benchmark:

| Resource | Why excluded |
|----------|--------------|
| **Crain's Petrophysical Handbook** | Copyrighted. Terms explicitly prohibit copying into datasets. |
| **SPE Petroleum Engineering Handbook** | Fully copyrighted. No redistribution rights. |
| **Tarek Ahmed's Reservoir Engineering Handbook** | Commercial publisher (Elsevier). Copyrighted. |

These can be used as **reference for human verification** but NOT for dataset content.

---

## Concept-Based Derivation (BYO Model)

Even from **copyrighted sources** (used privately), you can create original questions using the `concept_based` approach:

- **Allowed:** Questions written from scratch based on concepts/facts learned
- **Prohibited:** Verbatim copying, close paraphrases, reproducing unique problem structures

This means you can legally read any textbook and generate original MCQs — just don't copy the source's phrasing or distinctive problems. See main README.md for full policy on `derivation_mode`.

---

## Glossary

| Term | Meaning |
|------|---------|
| **CC** | Creative Commons — a family of open licenses |
| **BY** | Attribution required (credit the author) |
| **NC** | Non-Commercial use only |
| **SA** | Share-Alike (derivatives must use same license) |
| **ND** | No Derivatives (cannot modify — avoid for benchmarks) |
| **Public Domain** | No copyright. Completely free to use. |
| **Open Access** | Freely available, but check specific terms. |
| **OCW** | Open CourseWare (university course materials) |
| **BYO** | Bring Your Own — private sources you legally own |

**Common combinations:**
- `CC BY` — use freely, just credit author
- `CC BY-SA` — use freely, credit author, share derivatives under same license
- `CC BY-NC` — use freely for non-commercial, credit author
- `CC BY-NC-SA` — non-commercial + share-alike + attribution

---

## Adding New Sources

Criteria:
1. Explicit open license on the page (CC BY/SA/NC, Public Domain, Open Access)
2. No ND (NoDerivatives) for items intended for public release
3. Downloadable content from reputable host (university, gov, LibreTexts)
4. Relevant to: petrophysics, petroleum geology, geophysics, reservoir engineering, drilling
