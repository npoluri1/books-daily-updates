"""Vector search service using ChromaDB (free, local) for semantic book search."""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import threading

CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class VectorSearchService:
    _instance = None
    _collection = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_initialized(self):
        if self._initialized:
            return True
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self._client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            try:
                self._collection = self._client.get_collection("books")
            except Exception:
                self._collection = self._client.create_collection(
                    name="books",
                    metadata={"hnsw:space": "cosine"},
                )
            self._initialized = True
            return True
        except Exception as e:
            print(f"ChromaDB init error: {e}")
            return False

    def index_books(self, books: List[Dict]) -> int:
        if not self._ensure_initialized():
            return 0
        try:
            existing = self._collection.count()
            if existing > 0:
                return existing

            ids = []
            documents = []
            metadatas = []
            for book in books:
                doc_parts = [
                    book.get("title", ""),
                    book.get("author", ""),
                    book.get("description", ""),
                ]
                doc = " | ".join(p for p in doc_parts if p)
                if not doc.strip():
                    continue
                ids.append(str(book["id"]))
                documents.append(doc)
                metadatas.append({
                    "title": book.get("title", ""),
                    "author": book.get("author", "") or "",
                    "price": str(book.get("price", 0)),
                    "isbn": book.get("isbn", "") or "",
                })

            if documents:
                self._collection.add(ids=ids, documents=documents, metadatas=metadatas)
            return len(documents)
        except Exception as e:
            print(f"Index error: {e}")
            return 0

    def search(self, query: str, n_results: int = 10) -> List[Dict]:
        if not self._ensure_initialized():
            return []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            if not results["ids"] or not results["ids"][0]:
                return []

            output = []
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                output.append({
                    "id": int(doc_id),
                    "title": meta.get("title", ""),
                    "author": meta.get("author", ""),
                    "price": float(meta.get("price", 0)),
                    "similarity": results["distances"][0][i] if results["distances"] else 0,
                })
            return output
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_similar_books(self, book_id: int, n_results: int = 6) -> List[Dict]:
        if not self._ensure_initialized():
            return []
        try:
            book_doc = self._collection.get(ids=[str(book_id)])
            if not book_doc["documents"]:
                return []
            results = self._collection.query(
                query_texts=[book_doc["documents"][0]],
                n_results=n_results + 1,
            )
            if not results["ids"] or not results["ids"][0]:
                return []

            output = []
            for i, doc_id in enumerate(results["ids"][0]):
                if doc_id == str(book_id):
                    continue
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                output.append({
                    "id": int(doc_id),
                    "title": meta.get("title", ""),
                    "author": meta.get("author", ""),
                    "price": float(meta.get("price", 0)),
                    "similarity": results["distances"][0][i] if results["distances"] else 0,
                })
                if len(output) >= n_results:
                    break
            return output
        except Exception as e:
            print(f"Similar books error: {e}")
            return []

    def reindex(self, books: List[Dict]) -> int:
        if not self._ensure_initialized():
            return 0
        try:
            self._client.delete_collection("books")
            self._collection = self._client.create_collection("books")
            return self.index_books(books)
        except Exception as e:
            print(f"Reindex error: {e}")
            return 0

    @property
    def count(self) -> int:
        if not self._ensure_initialized():
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0


vector_search = VectorSearchService()
