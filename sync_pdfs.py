# sync_pdfs.py
import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

# --- UPDATED SLUGIFY FUNCTION ---
def slugify(title):
    """Converts a string into a URL-friendly slug."""
    title = title.lower()
    # Now replaces both spaces AND underscores with a hyphen
    title = title.replace(' ', '-').replace('_', '-')
    # Remove any other invalid characters
    title = re.sub(r'[^\w-]+', '', title)
    return title

def sync_pdf_filenames():
    print("Starting PDF sync process...")
    try:
        # 1. Get all files from storage
        storage_files_res = supabase.storage.from_('book-pdfs').list()
        if not storage_files_res:
            print("No files found in 'book-pdfs' bucket.")
            return
        storage_filenames = {file['name'] for file in storage_files_res}
        print(f"Found {len(storage_filenames)} files in storage.")

        # 2. Get all books from the database
        books_res = supabase.table('books').select('id, BOOK_TITLE').execute()
        if not books_res.data:
            print("No books found in the database.")
            return
        books = books_res.data
        print(f"Found {len(books)} books in the database.")

        # 3. Match files to books and update
        updates_made = 0
        for book in books:
            book_id = book['id']
            book_title = book['BOOK_TITLE']
            expected_pdf_name = f"{slugify(book_title)}.pdf"

            if expected_pdf_name in storage_filenames:
                print(f"Match found! Updating '{book_title}' with filename '{expected_pdf_name}'...")
                supabase.table('books').update({'PDF_FILENAME': expected_pdf_name}).eq('id', book_id).execute()
                updates_made += 1
            else:
                print(f"No matching PDF found for '{book_title}' (expected '{expected_pdf_name}').")

        print(f"\nSync complete. Made {updates_made} updates.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    sync_pdf_filenames()