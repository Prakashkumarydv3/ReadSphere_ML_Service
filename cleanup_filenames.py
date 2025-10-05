# cleanup_filenames.py
import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials
# Note: Ensure your .env file has these exact variable names
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY") # This should be your service_role key

# Check if credentials are set
if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in your .env file.")
    exit()

# Create a Supabase client
supabase: Client = create_client(url, key)
BUCKET_NAME = 'book-pdfs'

def clean_filename(name):
    """Applies a series of rules to clean up a filename."""
    
    # Keep the original extension, e.g., ".pdf"
    base_name, extension = os.path.splitext(name)

    # --- Rule 1: Convert to lowercase ---
    # This simplifies all subsequent text matching.
    base_name = base_name.lower()

    # --- Rule 2: Remove common junk prefixes ---
    prefixes_to_remove = ['oceanofpdf.com_', '_oceanofpdf.com_']
    for prefix in prefixes_to_remove:
        if base_name.startswith(prefix):
            base_name = base_name.replace(prefix, '', 1)

    # --- Rule 3: Remove appended junk after a clear separator ---
    # This looks for patterns like '_-_' and removes everything after it.
    # This is much safer than the previous version.
    if '_-_' in base_name:
        base_name = base_name.split('_-_')[0]

    # --- Rule 4: Replace spaces and underscores with a single hyphen ---
    # This is the main change you requested.
    base_name = re.sub(r'[\s_]+', '-', base_name)
    
    # --- Rule 5: Remove any other characters that are not letters, numbers, or hyphens ---
    base_name = re.sub(r'[^a-z0-9-]+', '', base_name)
    
    # --- Rule 6: Replace multiple hyphens with a single hyphen ---
    # Catches cases like "title---sub.pdf" and turns it into "title-sub.pdf"
    base_name = re.sub(r'-+', '-', base_name)

    # --- Rule 7: Remove any leading/trailing hyphens ---
    base_name = base_name.strip('-')

    # Ensure the base_name is not empty after cleaning
    if not base_name:
        return None # Or handle as an error, e.g., return original name

    return f"{base_name}{extension}"


def cleanup_storage_filenames():
    """Iterates through all files in a Supabase Storage bucket and renames them
    based on the cleaning rules."""
    
    print(f"Starting cleanup for bucket: '{BUCKET_NAME}'...")
    try:
        # Get all files from the storage bucket
        # Note: The modern Supabase Python client uses .from() instead of .from_()
        files = supabase.storage.from_(BUCKET_NAME).list()
        
        if not files:
            print("No files found in the bucket.")
            return

        for file_object in files:
            original_name = file_object['name']
            
            # Skip folders if any exist
            if 'id' not in file_object: 
                print(f"'{original_name}' appears to be a folder, skipping.")
                continue

            cleaned_name = clean_filename(original_name)
            
            if cleaned_name is None:
                print(f"Could not generate a valid name for '{original_name}', skipping.")
                continue

            # Only rename if the name has actually changed
            if original_name != cleaned_name:
                print(f"Renaming '{original_name}' -> '{cleaned_name}'")
                try:
                    # Use the 'move' command to rename the file
                    supabase.storage.from_(BUCKET_NAME).move(original_name, cleaned_name)
                except Exception as move_error:
                    print(f"  ERROR renaming '{original_name}': {move_error}")
            else:
                print(f"'{original_name}' is already clean. Skipping.")
                
        print("\nCleanup complete!")

    except Exception as e:
        print(f"An error occurred while listing files: {e}")

# Run the cleanup function
if __name__ == "__main__":
    cleanup_storage_filenames()