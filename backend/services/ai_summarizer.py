import json
import re
from typing import List, Optional, Dict, Any
from pathlib import Path


class AISummarizer:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is not None:
            return self._model
        import threading
        threading.Thread(target=self._load_model_async, daemon=True).start()
        return None

    def _load_model_async(self):
        try:
            from sentence_transformers import SentenceTransformer
            import logging
            logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
            self._model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        except Exception:
            self._model = None

    def generate_summary(self, book_title: str, chapter_number: int,
                         chapter_title: Optional[str] = None,
                         book_author: Optional[str] = None,
                         context: Optional[str] = None) -> Dict[str, Any]:
        title_info = f'"{book_title}"'
        if book_author:
            title_info += f" by {book_author}"
        chap = f"Chapter {chapter_number}"
        if chapter_title:
            chap += f": {chapter_title}"

        context_block = f"\n\nAdditional Context:\n{context}" if context else ""

        prompt = f"""You are a concise book summarizer. Summarize the key points from {title_info}, {chap}.

{context_block}

Format your response in this exact JSON structure:
{{
  "summary": "## TL;DR\\nOne-sentence summary of the chapter.\\n\\nThen 2-3 paragraphs covering the main concepts, developments, and insights. Write in clear, engaging prose suitable for mobile reading.",
  "key_points": [
    "Key takeaway 1: specific, actionable insight from this chapter",
    "Key takeaway 2: specific, actionable insight from this chapter",
    "Key takeaway 3: specific, actionable insight from this chapter",
    "Key takeaway 4: specific, actionable insight from this chapter",
    "Key takeaway 5: specific, actionable insight from this chapter"
  ],
  "reading_time_minutes": 5
}}"""

        return self._call_llm(prompt, chapter_number)

    def _call_llm(self, prompt: str, chapter_number: int) -> Dict[str, Any]:
        result = self._try_huggingface(prompt)
        if result:
            return result
        result = self._try_ollama(prompt)
        if result:
            return result
        return self._generate_fallback(chapter_number)

    def _try_huggingface(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            import httpx
            HF_TOKEN = None
            try:
                from backend.config import settings
                HF_TOKEN = settings.hf_token
            except Exception:
                pass

            headers = {"Content-Type": "application/json"}
            if HF_TOKEN:
                headers["Authorization"] = f"Bearer {HF_TOKEN}"

            model = "mistralai/Mistral-7B-Instruct-v0.2"
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.7,
                    "return_full_text": False,
                }
            }

            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
                    return self._parse_json_from_text(text)

                if resp.status_code == 503:
                    estimated = resp.json().get("estimated_time", 30)
                    import time
                    time.sleep(min(estimated, 30))
                    resp = client.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data[0].get("generated_text", "") if isinstance(data, list) else data.get("generated_text", "")
                        return self._parse_json_from_text(text)
        except Exception:
            pass
        return None

    def _try_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            import httpx
            payload = {
                "model": "llama3.2",
                "prompt": f"Respond ONLY with valid JSON. {prompt}",
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1024},
            }
            with httpx.Client(timeout=60) as client:
                resp = client.post("http://localhost:11434/api/generate", json=payload)
                if resp.status_code == 200:
                    text = resp.json().get("response", "")
                    return self._parse_json_from_text(text)
        except Exception:
            pass
        return None

    def _parse_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        return None

    def _generate_fallback(self, chapter_number: int) -> Dict[str, Any]:
        return {
            "summary": (
                f"Chapter {chapter_number} explores key concepts and developments "
                f"that advance the narrative and themes of the work. "
                f"The chapter introduces important ideas that build upon previous content "
                f"while setting up future developments. Key characters and concepts are "
                f"developed through meaningful interactions and revelations."
            ),
            "key_points": [
                "Chapter introduces new concepts central to the work's themes",
                "Character and plot developments advance the narrative",
                "Important thematic elements are explored in depth",
                "Connections to broader concepts are established",
                "Foundation laid for subsequent chapters",
            ],
            "reading_time_minutes": 5,
        }


summarizer = AISummarizer()
