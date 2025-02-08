import zipfile
import os
import glob
import re
from bs4 import BeautifulSoup
import pyperclip

# Directory containing EPUB files
epub_folder = "./"
output_folder = "./output_texts"
extract_base = "./extracted_epubs"

# Ensure output folders exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(extract_base, exist_ok=True)

# Get all EPUB files in the folder
epub_files = glob.glob(os.path.join(epub_folder, "*.epub"))

for epub_path in epub_files:
    # Extract filename without extension (for naming)
    epub_name = os.path.splitext(os.path.basename(epub_path))[0]
    extract_dir = os.path.join(extract_base, epub_name)

    # Step 1: Extract EPUB contents
    with zipfile.ZipFile(epub_path, "r") as epub:
        epub.extractall(extract_dir)

    # Step 2: Get all chapter files
    files = glob.glob(os.path.join(extract_dir, "OEBPS", "Text", "chapter*.xhtml"))

    # Extract numeric and optional letter part, then sort accordingly
    def extract_chapter_key(filename):
        match = re.search(r"chapter(\d+)([a-z]*)\.xhtml", filename, re.IGNORECASE)
        if match:
            num_part = int(match.group(1))  # Numeric part
            letter_part = match.group(2)  # Alphabetical part (e.g., "a", "b", "")
            return (num_part, letter_part)
        return (float("inf"), "")  # Unmatching files go last

    # Sort files correctly
    files.sort(key=extract_chapter_key)

    all_paragraphs = []

    # Step 3: Process XHTML files
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        all_paragraphs.extend(paragraphs)

    # Step 4: Combine into one text file
    combined_text = "\n".join(all_paragraphs)

    # Save to a text file (e.g., `book1.txt`, `book2.txt`)
    output_txt = os.path.join(output_folder, f"{epub_name}.txt")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(combined_text)

    # Copy to clipboard (last book processed)
    pyperclip.copy(combined_text)

    print(f"✅ Processed '{epub_name}.epub' → Saved as '{epub_name}.txt'")

print("🎉 All EPUB files processed!")
