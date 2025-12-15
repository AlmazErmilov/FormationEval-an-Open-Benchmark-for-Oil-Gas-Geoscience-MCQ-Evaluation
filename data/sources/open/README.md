# Open-Licensed Sources

Registry of open-licensed materials for public MCQ generation. Actual PDFs/materials go in this folder alongside this README.

---

## Source Catalog

| Domain | Resource | License | Risk | Good for | Link |
|--------|----------|---------|------|----------|------|
| Reservoir Engineering | **Petroleum Reservoir Dynamics** (Zeidouni, LSU) | CC BY-NC 4.0 | NC only | Darcy flow, transient analysis, well tests. Includes chapter quizzes. | [LSU Repository](https://repository.lsu.edu/etext/4/) |
| PVT / Thermodynamics | **Phase Relations in Reservoir Engineering** (Adewumi, Penn State) | CC BY-NC-SA 4.0 | NC only | Phase behavior, EOS, phase diagrams, VLE calculations. | [LibreTexts](https://eng.libretexts.org/Bookshelves/Chemical_Engineering/Phase_Relations_in_Reservoir_Engineering_(Adewumi)) |
| Mathematics | **Applied Mathematics in Reservoir Engineering** (Archer, Stanford) | Open Courseware | Verify | Derivations, diffusivity equation, dimensionless variables, Laplace transforms. | [Stanford PE 281](https://pangea.stanford.edu/ERE/research/ERE.html) |
| Simulation | **Introduction to Reservoir Simulation Using MATLAB/GNU Octave** (Lie, SINTEF) | Open Access | Unrestricted | Code generation, MRST scripts, grid generation, flow solvers. | [Cambridge Open Access](https://www.cambridge.org/core/books/an-introduction-to-reservoir-simulation-using-matlabgnu-octave/F48C3D8C88A3F67E4D97D4E16970F894) |
| Petrophysics | **Borehole Geophysics Applied to Ground-Water Investigations** (Keys, USGS) | Public Domain | Unrestricted | Tool physics: GR, Neutron, Density, Sonic, Resistivity. Log interpretation. | [USGS TWRI 2-E2](https://pubs.usgs.gov/twri/twri2-e2/) |
| Petrophysics | **Principles of Formation Evaluation** (NPTEL / IIT) | CC BY-SA | Unrestricted | Modern tools: NMR, FMI/image logs. Shaly sand models (Simandoux, Indonesian). | [NPTEL Course](https://archive.nptel.ac.in/courses/103/105/103105158/) |
| Petroleum Geology | **Petroleum Geology** (TU Delft OCW) | CC BY-NC-SA 4.0 | NC only | Petroleum systems, basin analysis, exploration workflow. | [TU Delft OCW](https://ocw.tudelft.nl/courses/petroleum-geology/) |
| Sedimentology | **Sedimentary Geology** (Rygel & Quinton, SUNY) | CC BY-SA 4.0 | Unrestricted | Visual interpretation, sedimentary structures, facies analysis. Image-rich. | [LibreTexts](https://geo.libretexts.org/Courses/SUNY_Potsdam/Sedimentary_Geology) |
| Drilling | **Drilling Fluid Engineering** (Skalle, NTNU) | Open Access | Verify | Rheology, hydraulics, hole cleaning, mud properties. | [Bookboon](https://bookboon.com/en/drilling-fluid-engineering-ebook) |
| CCUS (future) | **Carbon Storage Atlas V** (NETL / DOE) | Public Domain | Unrestricted | CO2 storage capacity, saline aquifers, depleted reservoirs. Energy transition. | [NETL Atlas](https://netl.doe.gov/coal/carbon-storage/strategic-program-support/natcarb-atlas) |

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
