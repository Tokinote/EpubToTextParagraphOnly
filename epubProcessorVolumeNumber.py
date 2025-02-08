import zipfile
import os
import glob
import re
from bs4 import BeautifulSoup

# Directory containing EPUB files
epub_folder = "./"
output_folder = "./output_texts"
extract_base = "./extracted_epubs"

# Ensure output folders exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(extract_base, exist_ok=True)

# Get all EPUB files in the folder
epub_files = glob.glob(os.path.join(epub_folder, "*.epub"))

for idx, epub_path in enumerate(epub_files, start=1):
    volume_name = f"volume{idx}"  # Volume naming (volume1, volume2, etc.)
    extract_dir = os.path.join(extract_base, volume_name)

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

    # Save as volume1.txt, volume2.txt, etc.
    output_txt = os.path.join(output_folder, f"{volume_name}.txt")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(combined_text)


    print(f"✅ Processed '{os.path.basename(epub_path)}' → Saved as '{volume_name}.txt'")

print("🎉 All EPUB files processed and saved as volume1, volume2, etc.")
