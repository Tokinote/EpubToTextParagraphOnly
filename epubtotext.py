import zipfile
import os
import glob
import re
import sys
from bs4 import BeautifulSoup

def extract_epub_from_memory(epub_path):
    """
    Extracts and processes XHTML content from an EPUB file in-memory.

    :param epub_path: Path to the EPUB file.
    :return: Extracted text as a string.
    """
    all_paragraphs = []

    try:
        with zipfile.ZipFile(epub_path, "r") as epub:
            # Find all XHTML chapter files inside the EPUB
            chapter_files = sorted(
                [f for f in epub.namelist() if re.search(r"chapter\d+[a-z]*\.xhtml", f, re.IGNORECASE)],
                key=lambda x: re.findall(r"chapter(\d+)([a-z]*)", x, re.IGNORECASE)
            )

            if not chapter_files:
                print(f"⚠ No valid chapters found in {os.path.basename(epub_path)}. Skipping.")
                return None

            # Process each chapter file in-memory
            for file in chapter_files:
                with epub.open(file) as f:
                    soup = BeautifulSoup(f.read(), "html.parser")

                paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
                all_paragraphs.extend(paragraphs)

    except Exception as e:
        print(f"❌ Error processing {os.path.basename(epub_path)}: {e}")
        return None

    return "\n".join(all_paragraphs)

def convert_epubs_to_txt(epub_folder):
    """
    Converts all EPUB files in the given folder to TXT format.

    :param epub_folder: Path to the folder containing EPUB files.
    """
    output_folder = os.path.join(epub_folder, "txt_output")
    os.makedirs(output_folder, exist_ok=True)

    # Get all EPUB files
    epub_files = sorted(glob.glob(os.path.join(epub_folder, "*.epub")))

    if not epub_files:
        print("⚠ No EPUB files found in the provided folder.")
        return

    for epub_path in epub_files:
        epub_name = os.path.splitext(os.path.basename(epub_path))[0]  # Extract name without .epub
        output_txt_path = os.path.join(output_folder, f"{epub_name}.txt")

        extracted_text = extract_epub_from_memory(epub_path)

        if extracted_text:
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)


            print(f"✅ Processed '{os.path.basename(epub_path)}' → Saved as '{epub_name}.txt'")

    print("🎉 All EPUB files processed and saved in 'txt_output/'.")

# Command-line argument handling
if len(sys.argv) != 2:
    print("Usage: python epubtotxt.py <epub_folder>")
    sys.exit(1)

epub_folder = sys.argv[1]

if not os.path.isdir(epub_folder):
    print(f"❌ Error: '{epub_folder}' is not a valid directory.")
    sys.exit(1)

convert_epubs_to_txt(epub_folder)
