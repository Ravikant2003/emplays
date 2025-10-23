from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup


@dataclass
class HTMLParseResult:
    text: str
    metadata: Dict[str, Any]


def parse_html_content(html: str, base_url: Optional[str] = None) -> HTMLParseResult:
    soup = BeautifulSoup(html, "html.parser")
    # Get visible text
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())

    meta = {
        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
        "base_url": base_url,
    }
    return HTMLParseResult(text=text, metadata=meta)
