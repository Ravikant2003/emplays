from __future__ import annotations
from typing import Optional, Dict, Any
import os

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class FlanT5Extractor:
    def __init__(self, model_name: str = "google/flan-t5-base", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self._tokenizer = None
        self._model = None

    def load(self) -> None:
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self._model is None:
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        if self.device:
            self._model.to(self.device)

    def extract_json(self, prompt: str, max_new_tokens: int = 512) -> str:
        if self._model is None or self._tokenizer is None:
            self.load()
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.0,
        )
        return self._tokenizer.decode(outputs[0], skip_special_tokens=True)
