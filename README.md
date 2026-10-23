# Hidden in plain sight: cyberbullying of adolescents (2020–2026)

An evidence dashboard that tells the story of adolescent cyberbullying and cyber victimization, from the world to India, structured on the Stanford d.school design-thinking modes: Empathize, Define, Ideate, Prototype, Test.

Every number on the page comes from a row of `evidence_ledger.csv`. Under each chart, an evidence block shows the source, location in the source, data year, how the number was checked, and the exact quote. Figures calculated by the dashboard are labelled "computed" and show their formula.

## View it

- **Online (GitHub Pages):** open the Pages URL for this repo. Python runs in the browser via [stlite](https://github.com/whitphx/stlite), so the first load can take 10–30 seconds.
- **Locally:**
  ```bash
  pip install -r requirements.txt
  streamlit run dashboard.py
  ```

## Files

| File | Purpose |
|---|---|
| `dashboard.py` | The Streamlit dashboard |
| `evidence_ledger.csv` | The evidence ledger: one row per number, with source, location, data year and verification |
| `build_ledger.py` | Script that generated the ledger from source text (needs the original source files, not included) |
| `index.html` | Runs `dashboard.py` in the browser for GitHub Pages |
| `requirements.txt` | Python packages for running locally |
