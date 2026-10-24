# Hidden in plain sight: cyberbullying of adolescents (2020–2026)

An evidence dashboard that tells the story of adolescent cyberbullying and cyber victimization, from the world to India, structured on the Stanford d.school design-thinking modes: Empathize, Define, Ideate, Prototype, Test.

Every number on the page comes from a row of `evidence_ledger.csv`, and every row carries a clickable link to its source, its location in the source (table, page or section), the data year and the exact quote it was checked against. Under each chart, an evidence block links the sources behind that chart and, where useful, related 2025–26 evidence. Figures calculated by the dashboard are labelled "computed" and show their formula. The full ledger and a source registry sit in the dashboard's annexure.

## View it

- **Online (GitHub Pages):** https://ptnov218-nlu.github.io/Cybercrime-dashboad/ — Python runs in the browser via [stlite](https://github.com/whitphx/stlite), so the first load can take 30–90 seconds.
- **Locally:**
  ```bash
  pip install -r requirements.txt
  streamlit run dashboard.py
  ```

## Files

| File | Purpose |
|---|---|
| `dashboard.py` | The Streamlit dashboard |
| `evidence_ledger.csv` | The evidence ledger: one row per number, with source link, publisher page, location, data year, verification and exact quote |
| `build_ledger.py` | Defines every source and row, and rebuilds the ledger, checking each quote against plain-text copies of the sources (`python build_ledger.py --text-dir <folder>`) |
| `index.html` | Runs `dashboard.py` in the browser for GitHub Pages |
| `requirements.txt` | Python packages for running locally |

## Sources

WHO/Europe HBSC 2021/22; UNICEF Innocenti (Childhood in a Digital World 2025; Global Kids Online 2019); OECD PISA 2025; WeProtect Global Threat Assessment 2023; UNESCO GEM Report 2024/5; NCRB Crime in India 2023 and 2024; PIB Lok Sabha replies (Jul 2025, Jul 2026); Bahl et al., PLOS ONE 2026 (Himachal Pradesh); Kharadi et al., Bioinformation 2025; NCPCR guidance documents. Links for each are in the ledger and the dashboard annexure.
