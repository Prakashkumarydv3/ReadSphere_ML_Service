# seed.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Create a Supabase client
supabase: Client = create_client(url, key)

# --- Add all your books to this list ---
books_to_add = [
    {
        "BOOK_TITLE": "The Midnight Library",
        "BOOK_AUTHOR": "Matt Haig",
        "GENRE": "Fantasy",
        "A_RATINGS": 4.5,
        "F_PAGE": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1602190253l/52578297.jpg",
        "LINK": "https://www.goodreads.com/book/show/52578297-the-midnight-library"
    },
    {
        "BOOK_TITLE": "Project Hail Mary",
        "BOOK_AUTHOR": "Andy Weir",
        "GENRE": "Science Fiction",
        "A_RATINGS": 4.8,
        "F_PAGE": "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1597695864l/54493401.jpg",
        "LINK": "https://www.goodreads.com/book/show/54493401-project-hail-mary"
    },
    # --- Add your other 18+ books here in the same format ---
]

def seed_database():
    print("Starting to seed the database...")
    for book in books_to_add:
        try:
            data, count = supabase.table('books').insert(book).execute()
            print(f"Successfully inserted: {book['BOOK_TITLE']}")
        except Exception as e:
            print(f"Could not insert {book['BOOK_TITLE']}. Error: {e}")
    
    print("Database seeding complete.")

# Run the function
if __name__ == "__main__":
    seed_database()