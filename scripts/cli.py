from __future__ import annotations
import argparse
from pathlib import Path
from typing import List
import sys, os

import requests

# Ensure package imports work when running from repo
CURRENT_DIR = Path(__file__).resolve()
REPO_ROOT = CURRENT_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rfp_extractor.parsers.web_loader import load_dynamic_page
from rfp_extractor.parsers.html_parser import parse_html_content
from rfp_extractor.parsers.pdf_parser import parse_pdf_bytes
from rfp_extractor.extraction.pipeline import ExtractionPipeline
from rfp_extractor.extraction.io import save_json


def process_file(path: Path, pipeline: ExtractionPipeline, output_dir: Path) -> None:
    ext = path.suffix.lower()
    if ext == ".html" or ext == ".htm":
        text = parse_html_content(path.read_text(encoding="utf-8", errors="ignore")).text
    elif ext == ".pdf":
        text = parse_pdf_bytes(path.read_bytes()).text
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
    data = pipeline.extract(text)
    out_path = output_dir / f"{path.stem}.json"
    save_json(data, out_path)
    print(f"Saved: {out_path}")


def process_url(url: str, pipeline: ExtractionPipeline, output_dir: Path) -> None:
    if url.lower().endswith(".pdf"):
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        text = parse_pdf_bytes(resp.content).text
    else:
        html = load_dynamic_page(url).html
        text = parse_html_content(html, base_url=url).text
    data = pipeline.extract(text)
    safe_name = (
        url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_")
    )[:80]
    out_path = output_dir / f"{safe_name}.json"
    save_json(data, out_path)
    print(f"Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="RFP extractor")
    parser.add_argument("inputs", nargs="+", help="Files or URLs")
    parser.add_argument("--model", default="google/flan-t5-base")
    parser.add_argument("--device", default=None)
    parser.add_argument("--out", default="outputs")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM and use heuristics only")
    parser.add_argument("--use-rag", action="store_true", help="Enable RAG (BM25 retriever) to ground the prompt")
    parser.add_argument("--rag-top-k", type=int, default=8, help="Number of passages to retrieve for RAG")
    parser.add_argument("--rag-hint", type=str, default="", help="Optional query hint to steer retrieval")
    args = parser.parse_args()

    if args.no_llm:
        llm = None
    else:
        # Lazy import to avoid requiring transformers/torch when disabled
        try:
            from rfp_extractor.llm.flan_t5 import FlanT5Extractor  # type: ignore
            llm = FlanT5Extractor(model_name=args.model, device=args.device)
        except Exception as e:  # Graceful fallback when transformers is unavailable
            print(f"Warning: LLM disabled due to import/load error: {e}", file=sys.stderr)
            llm = None
    pipeline = ExtractionPipeline(
        llm=llm,
        rag_enabled=bool(args.use_rag),
        rag_top_k=int(args.rag_top_k),
        rag_query_hint=(args.rag_hint or None),
    )

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    for inp in args.inputs:
        if inp.startswith("http://") or inp.startswith("https://"):
            process_url(inp, pipeline, output_dir)
        else:
            process_file(Path(inp), pipeline, output_dir)


if __name__ == "__main__":
    main()
