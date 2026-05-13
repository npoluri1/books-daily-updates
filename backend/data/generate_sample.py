import pandas as pd
from pathlib import Path

samples = [
    {
        "books": [
            {"title": "Atomic Habits", "author": "James Clear", "isbn": "9780735211292", "total_chapters": 20},
            {"title": "The Lean Startup", "author": "Eric Ries", "isbn": "9780307887894", "total_chapters": 15},
            {"title": "Deep Work", "author": "Cal Newport", "isbn": "9781455586691", "total_chapters": 12},
            {"title": "Think and Grow Rich", "author": "Napoleon Hill", "isbn": "9781585424337", "total_chapters": 17},
            {"title": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey", "isbn": "9781982137274", "total_chapters": 13},
            {"title": "How to Win Friends and Influence People", "author": "Dale Carnegie", "isbn": "9780671027032", "total_chapters": 14},
            {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "isbn": "9780062316110", "total_chapters": 20},
            {"title": "The Psychology of Money", "author": "Morgan Housel", "isbn": "9780857197689", "total_chapters": 19},
            {"title": "Rich Dad Poor Dad", "author": "Robert T. Kiyosaki", "isbn": "9781612680194", "total_chapters": 10},
            {"title": "The Alchemist", "author": "Paulo Coelho", "isbn": "9780062315007", "total_chapters": 12},
        ]
    },
    {
        "books": [
            {"title": "Zero to One", "author": "Peter Thiel", "isbn": "9780804139298", "total_chapters": 14},
            {"title": "The Power of Habit", "author": "Charles Duhigg", "isbn": "9780812981605", "total_chapters": 12},
            {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "isbn": "9780374533557", "total_chapters": 38},
            {"title": "The Compound Effect", "author": "Darren Hardy", "isbn": "9781937077166", "total_chapters": 10},
            {"title": "Start with Why", "author": "Simon Sinek", "isbn": "9781591846444", "total_chapters": 15},
            {"title": "Good to Great", "author": "Jim Collins", "isbn": "9780066620992", "total_chapters": 12},
            {"title": "The 4-Hour Work Week", "author": "Tim Ferriss", "isbn": "9780307465351", "total_chapters": 18},
            {"title": "Man's Search for Meaning", "author": "Viktor E. Frankl", "isbn": "9780807014295", "total_chapters": 8},
            {"title": "Daring Greatly", "author": "Brené Brown", "isbn": "9781592407330", "total_chapters": 11},
            {"title": "The Art of War", "author": "Sun Tzu", "isbn": "9781590302255", "total_chapters": 13},
        ]
    }
]

output_dir = Path(__file__).parent
for i, sample in enumerate(samples, 1):
    df = pd.DataFrame(sample["books"])
    path = output_dir / f"books_list_{i}.xlsx"
    df.to_excel(path, index=False)
    print(f"Created: {path.name} ({len(sample['books'])} books)")

print("\nSample Excel files created. Upload these via the app!")
