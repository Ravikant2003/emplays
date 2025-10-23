from __future__ import annotations
import io
from pathlib import Path

import streamlit as st

from rfp_extractor.parsers.web_loader import load_dynamic_page
from rfp_extractor.parsers.html_parser import parse_html_content
from rfp_extractor.parsers.pdf_parser import parse_pdf_bytes
from rfp_extractor.extraction.pipeline import ExtractionPipeline


st.set_page_config(page_title="RFP Extractor", layout="wide")

st.title("RFP Structured Data Extractor")

with st.sidebar:
    model = st.text_input("Flan-T5 model", value="google/flan-t5-base")
    device = st.selectbox("Device", [None, "cpu"], index=1)
    st.caption("Uses heuristic + LLM extraction with synonyms prompts.")
    st.divider()
    st.markdown("**Retrieval-Augmented Generation (RAG)**")
    use_rag = st.toggle("Use RAG (BM25 retriever)", value=False)
    rag_top_k = st.number_input("RAG top-k passages", min_value=1, max_value=20, value=8, step=1)
    rag_hint = st.text_input("Optional RAG query hint", value="")

@st.cache_resource(show_spinner=False)
def get_pipeline(
    model_name: str,
    device_opt: str | None,
    use_llm: bool,
    use_rag: bool,
    rag_top_k: int,
    rag_hint: str,
) -> ExtractionPipeline:
    llm = None
    if use_llm:
        try:
            from rfp_extractor.llm.flan_t5 import FlanT5Extractor  # lazy import
            llm = FlanT5Extractor(model_name=model_name, device=device_opt)
        except Exception as e:
            st.warning(f"LLM disabled due to import/load error: {e}")
            llm = None
    return ExtractionPipeline(
        llm=llm,
        rag_enabled=use_rag,
        rag_top_k=int(rag_top_k),
        rag_query_hint=(rag_hint or None),
    )

use_llm = st.toggle("Use LLM (Flan‑T5)", value=False)
pipeline = get_pipeline(model, device, use_llm, use_rag, rag_top_k, rag_hint)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Document")
    uploaded = st.file_uploader("Upload HTML or PDF", type=["html", "htm", "pdf"]) 
    if uploaded is not None:
        if uploaded.type == "application/pdf" or uploaded.name.lower().endswith(".pdf"):
            text = parse_pdf_bytes(uploaded.read()).text
        else:
            content = uploaded.read().decode("utf-8", errors="ignore")
            text = parse_html_content(content).text
        with st.expander("Raw Text", expanded=False):
            st.text_area("text", text, height=300)
        if st.button("Extract from Upload"):
            with st.spinner("Extracting..."):
                data = pipeline.extract(text)
            st.json(data.dict(by_alias=True, exclude_none=True))

with col2:
    st.subheader("Fetch by URL")
    url = st.text_input("Enter RFP page or PDF URL")
    wait_css = st.text_input("Optional CSS to wait for", value="")
    if st.button("Load & Extract") and url:
        with st.spinner("Loading page..."):
            if url.lower().endswith(".pdf"):
                import requests
                resp = requests.get(url, timeout=60)
                resp.raise_for_status()
                text = parse_pdf_bytes(resp.content).text
            else:
                html = load_dynamic_page(url, wait_css=wait_css or None).html
                text = parse_html_content(html, base_url=url).text
        with st.expander("Raw Text", expanded=False):
            st.text_area("text", text, height=300)
        with st.spinner("Extracting..."):
            data = pipeline.extract(text)
        st.json(data.dict(by_alias=True, exclude_none=True))
