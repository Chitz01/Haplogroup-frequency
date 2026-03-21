# 🧬 Haplogroup Frequency Explorer

> An interactive web application for visualising ancient DNA haplogroup distributions and migration patterns using the AADR 2025 dataset.

---

## What is this app?

The **Haplogroup Frequency Explorer** lets you query any Y-DNA or mtDNA haplogroup and instantly see where it was found in the ancient world — which countries, how frequently, how far back in time, and how it spread geographically.

Built on the **Allen Ancient DNA Resource (AADR) 2025** — the world's largest ancient DNA database — containing **15,252 individuals** from **most countries** spanning **108,500 BCE to 1,890 CE**.

---

## Why use this tool?

- 🔍 **Instant haplogroup search** — type any haplogroup (e.g. `R1b`, `H`, `U5`, `J2`) and get results in seconds
- 🌍 **World map** — choropleth map showing frequency per country at a glance
- 📊 **Bar chart** — top 15 countries ranked by haplogroup frequency
- 🏺 **Oldest samples** — find the 10 most ancient individuals carrying the haplogroup
- 🗺️ **Migration map** — arrows showing the chronological spread of the haplogroup across geography
- ⬇️ **CSV export** — download your results for further analysis
- 🔗 **Prefix matching** — searching `R1b` automatically includes `R1b1a`, `R1b1a2a1`, and all sub-branches

---

## Installation

**Requirements:** Python 3.10 or higher

Open a terminal and run:

```bash
# 1. Clone the repository
git clone https://github.com/Chitz01/Haplogroup-frequency.git
cd Haplogroup-frequency

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate          # Mac / Linux
.venv\Scripts\activate.bat         # Windows CMD
.venv\Scripts\Activate.ps1         # Windows PowerShell

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## Data

Download the AADR 2025 dataset 

Upload the file directly in the app sidebar — no setup needed.

---

## Quick start

Once the app is running:

1. Click **Browse files** in the sidebar and upload the AADR CSV file
2. Choose **Y-DNA** or **mtDNA**
3. Type a haplogroup in the search box

| Haplogroup | Type | Associated with |
|---|---|---|
| `R1b` | Y-DNA | Western Europe, Bronze Age steppe |
| `I1` | Y-DNA | Scandinavia |
| `J2` | Y-DNA | Near East, Mediterranean |
| `H` | mtDNA | Common in ancient Europe |
| `U5` | mtDNA | European hunter-gatherers |
| `D4` | mtDNA | East Asia |

4. Click **Search** and explore the results

---

## How it was built — development history

This project was built incrementally with one feature added per commit:

| Commit | What was added |
|---|---|
| Commit 1 | Basic page with title and description |
| Commit 2 | File upload and data table display |
| Commit 3 | Haplogroup search and bar chart |
| Commit 4 | World map showing haplogroup frequency |
| Commit 5 | Oldest samples table, summary metrics, CSV download |
| Commit 6 | Migration map showing haplogroup spread over time |

---

## Tech stack

| Tool | Purpose |
|---|---|
| [Python 3.13](https://python.org) | Core language |
| [Streamlit](https://streamlit.io) | Web interface |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Maps and charts |
| [Pandas](https://pandas.pydata.org) | Data manipulation |
| `csv` + `io` | Custom AADR file parser |
| [Git](https://git-scm.com) | Version control |

---

## Next time you want to run it

After the first setup, only three commands are needed:

```bash
cd Documents/LU/SEM2/BINP29/Haplogroup-frequency
source .venv/bin/activate
streamlit run app.py
```

---

## Project structure

```
Haplogroup-frequency/
├── app.py               ← Main application
├── requirements.txt     ← Python dependencies
└── README.md            ← This file
```

---

## Limitations

- Frequencies reflect **sampled ancient individuals**, not true population frequencies
- The AADR has **geographic sampling bias** — Europe is heavily overrepresented
- A country showing **100% frequency** may have only 1 individual sampled — check the counts
- Migration arrows show **chronological spread**, not proven direct ancestry

---

## References

Mallick, S. et al. (2023) The Allen Ancient DNA Resource (AADR): a curated compendium of ancient human genomes. *bioRxiv*, doi:10.1101/2023.04.06.535797

Haak, W. et al. (2015) Massive migration from the steppe was a source for Indo-European languages in Europe. *Nature*, **522**, 207–211.

---

## License

This project is open-source and free to use for academic and research purposes.

---

