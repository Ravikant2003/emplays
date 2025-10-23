## RFP Structured Data Extractor

Extract structured fields from RFP HTML/PDFs using heuristics + Flan‑T5. Includes a Streamlit UI and a batch CLI.

### Features
- HTML/PDF parsing (Selenium-rendered pages supported)
- Heuristic extraction + LLM (Flan‑T5) prompting
- Streamlit app for uploads and URLs
- CLI for batch processing to JSON outputs

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Selenium uses webdriver-manager to auto-install ChromeDriver. Ensure Chrome/Chromium is present.
On Debian/Ubuntu, to install Chromium:
```bash
sudo apt-get update && sudo apt-get install -y chromium-browser
```

### Streamlit App
```bash
streamlit run app/streamlit_app.py
```

### CLI Usage
```bash
python scripts/cli.py --out outputs docs/sample1.pdf https://example.com/rfp
```

### Output
Each processed input produces a JSON file in `outputs/` with keys matching the assignment fields.

### Notes
- Default model is `google/flan-t5-base`. You can change to any Flan‑T5 size.
- For CPU-only environments, set device to `cpu` in the app or pass `--device cpu` to the CLI.
- PDFs with complex layouts may need more advanced extraction; `pdfplumber` is a good baseline.
