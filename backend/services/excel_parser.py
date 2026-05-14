import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


def parse_excel_books(file_path: str) -> List[Dict[str, Any]]:
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    possible_title_cols = ["title", "book", "book_title", "name", "book_name", "bookname"]
    possible_author_cols = ["author", "author_name", "writer", "creator"]
    possible_isbn_cols = ["isbn", "isbn13", "isbn10", "book_id"]
    possible_chapters_cols = ["chapters", "total_chapters", "num_chapters", "chapter_count"]
    possible_price_cols = ["price", "cost", "amount", "selling_price"]
    possible_stock_cols = ["stock", "stock_quantity", "quantity", "qty", "inventory"]

    seen_titles = set()
    all_books = []

    for sheet_name in sheet_names:
        df = xls.parse(sheet_name, dtype=str)
        df = df.fillna("")

        if df.empty or df.columns.empty:
            continue

        title_col = _find_column(df.columns, possible_title_cols)
        if not title_col:
            title_col = df.columns[0]

        author_col = _find_column(df.columns, possible_author_cols)
        isbn_col = _find_column(df.columns, possible_isbn_cols)
        chapters_col = _find_column(df.columns, possible_chapters_cols)
        price_col = _find_column(df.columns, possible_price_cols)
        stock_col = _find_column(df.columns, possible_stock_cols)

        for _, row in df.iterrows():
            title = str(row[title_col]).strip()
            if not title or title.lower() == "nan":
                continue

            title_lower = title.lower()
            if title_lower in seen_titles:
                continue
            seen_titles.add(title_lower)

            author = str(row[author_col]).strip() if author_col and str(row[author_col]).strip().lower() != "nan" else ""
            isbn = str(row[isbn_col]).strip() if isbn_col and str(row[isbn_col]).strip().lower() != "nan" else ""
            chapters_str = str(row[chapters_col]).strip() if chapters_col else "0"
            total_chapters = 0
            try:
                total_chapters = int(float(chapters_str))
            except (ValueError, TypeError):
                pass
            price = 0.0
            if price_col:
                try:
                    price = float(str(row[price_col]).strip())
                except (ValueError, TypeError):
                    pass
            stock = 50
            if stock_col:
                try:
                    stock = int(float(str(row[stock_col]).strip()))
                except (ValueError, TypeError):
                    pass

            all_books.append({
                "title": title,
                "author": author if author else None,
                "isbn": isbn if isbn else None,
                "total_chapters": total_chapters,
                "price": price,
                "stock_quantity": stock,
            })

    return all_books


def _find_column(columns, possible_names: List[str]) -> Optional[str]:
    col_lower = {c.lower().strip(): c for c in columns}
    for name in possible_names:
        if name in col_lower:
            return col_lower[name]
    for col in columns:
        for name in possible_names:
            if name in col.lower().replace(" ", "_").replace("-", "_"):
                return col
    return None


def search_books_by_regex(books: List[Dict], pattern: str, use_regex: bool = False) -> List[Dict]:
    if not pattern:
        return books
    if use_regex:
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            return [b for b in books if compiled.search(b["title"])]
        except re.error:
            return []
    pattern_lower = pattern.lower()
    return [b for b in books if pattern_lower in b["title"].lower()]
