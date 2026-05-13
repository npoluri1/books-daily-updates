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
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            self._model = None
        return self._model

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

        prompt = f"""You are a literary analyst. Summarize {chap} of {title_info}.

Provide a structured response in this exact JSON format:
{{
  "summary": "A concise 3-5 paragraph summary of the chapter covering all major events, concepts, and developments. Write in clear, engaging prose.",
  "key_points": [
    "Key point 1: specific, actionable insight from the chapter",
    "Key point 2: specific, actionable insight from the chapter",
    "Key point 3: specific, actionable insight from the chapter",
    "Key point 4: specific, actionable insight from the chapter",
    "Key point 5: specific, actionable insight from the chapter"
  ],
  "reading_time_minutes": 5
}}"""

        return self._call_llm(prompt, chapter_number)

    def _call_llm(self, prompt: str, chapter_number: int) -> Dict[str, Any]:
        providers = [
            self._try_huggingface,
            self._try_ollama,
            self._try_fallback,
        ]

        for provider in providers:
            try:
                result = provider(prompt)
                if result:
                    return result
            except Exception:
                continue

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
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "return_full_text": False,
                }
            }

            with httpx.Client(timeout=60) as client:
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

    def _try_fallback(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            import httpx
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a literary analyst. Respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 1024,
                "temperature": 0.7,
            }
            try:
                from backend.config import settings
                api_key = settings.openrouter_key
                if api_key:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    resp = httpx.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        text = resp.json()["choices"][0]["message"]["content"]
                        return self._parse_json_from_text(text)
            except Exception:
                pass
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
