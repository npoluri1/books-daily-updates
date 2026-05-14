"""LangChain-powered AI recommendation engine (free, local)."""
import json
from typing import List, Dict, Optional, Any
from pathlib import Path


class BookRecommender:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _build_prompt(self, user_profile: Dict, available_books: List[Dict],
                      recent_orders: Optional[List[Dict]] = None) -> str:
        liked_cats = user_profile.get("liked_categories", [])
        liked_authors = user_profile.get("liked_authors", [])
        budget = user_profile.get("budget_max", 100)

        orders_text = ""
        if recent_orders:
            titles = []
            for o in recent_orders:
                for item in o.get("items", []):
                    book = item.get("book", {})
                    if book.get("title"):
                        titles.append(book["title"])
            if titles:
                orders_text = f"\nPreviously purchased: {', '.join(titles[:5])}"

        books_text = "\n".join(
            f"- {b.get('title', '')} by {b.get('author', 'Unknown')} "
            f"[{', '.join(c.get('name', '') for c in b.get('categories', []))}] "
            f"${b.get('price', 0):.2f}"
            for b in available_books[:30]
        )

        prompt = f"""You are a book recommendation engine. Based on the user profile and available books, recommend the best books.

User Profile:
- Liked categories: {', '.join(liked_cats) if liked_cats else 'None'}
- Preferred authors: {', '.join(liked_authors) if liked_authors else 'None'}
- Max budget: ${budget}{orders_text}

Available Books:
{books_text}

Return a JSON array of up to 6 book titles that best match this user, ranked by relevance.
Format: ["Title 1", "Title 2", ...]
Only return titles that exist in the available books list above."""

        return prompt

    def recommend_for_user(self, user_profile: Dict, available_books: List[Dict],
                           recent_orders: Optional[List[Dict]] = None) -> List[Dict]:
        prompt = self._build_prompt(user_profile, available_books, recent_orders)
        result = self._call_llm(prompt)
        if result and isinstance(result, list):
            recommended_titles = [r.lower().strip() for r in result]
            recommended = []
            seen = set()
            for title in recommended_titles:
                for book in available_books:
                    if book.get("title", "").lower().strip() == title:
                        if book["id"] not in seen:
                            recommended.append(book)
                            seen.add(book["id"])
                            break
            return recommended[:6]
        return self._fallback_recommendations(available_books, user_profile)

    def _call_llm(self, prompt: str) -> Optional[Any]:
        try:
            import httpx
            from backend.config import settings
            hf_token = settings.hf_token
            headers = {"Content-Type": "application/json"}
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {"max_new_tokens": 300, "temperature": 0.3, "return_full_text": False},
            }
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                    headers=headers, json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data[0].get("generated_text", "") if isinstance(data, list) else ""
                    return self._parse_json(text)
        except Exception:
            pass
        return None

    def _parse_json(self, text: str) -> Optional[Any]:
        import re
        if not text:
            return None
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return None

    def _fallback_recommendations(self, books: List[Dict], profile: Dict) -> List[Dict]:
        liked_cats = set(c.lower() for c in profile.get("liked_categories", []))
        budget = profile.get("budget_max", 100)

        scored = []
        for b in books:
            score = 0
            if liked_cats:
                book_cats = set(c.get("name", "").lower() for c in b.get("categories", []))
                overlap = len(liked_cats & book_cats)
                score += overlap * 10
            if b.get("price", 0) <= budget:
                score += 5
            if b.get("stock_quantity", 0) > 0:
                score += 3
            scored.append((score, b))

        scored.sort(key=lambda x: -x[0])
        return [b for _, b in scored[:6]]


recommender = BookRecommender()
