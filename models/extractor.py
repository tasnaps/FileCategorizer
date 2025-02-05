# models/extractor.py
import os
import re
import logging
from urllib.parse import quote
import requests
from ebooklib import epub
from transformers import pipeline
from PyPDF2 import PdfReader

class EbookMetadataExtractor:
    def __init__(self, enable_title_cleaning=False, enable_author_extraction=False):
        self.enable_title_cleaning = enable_title_cleaning
        self.enable_author_extraction = enable_author_extraction
        if self.enable_author_extraction:
            try:
                self.instruction_model = pipeline("text2text-generation", model="google/flan-t5-base")
            except Exception as e:
                logging.error(f"Error initializing instruction model: {e}")
                self.instruction_model = None
        else:
            self.instruction_model = None

    def sanitize_text(self, text):
        if text is None:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def sanitize_filename(self, filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def extract_epub_metadata(self, file_path):
        try:
            book = epub.read_epub(file_path)
        except Exception as e:
            logging.error(f"Error reading EPUB {file_path}: {e}")
            return "", "", ""
        title, author, description = "", "", ""
        try:
            title_entries = book.get_metadata('DC', 'title')
            if title_entries:
                title = title_entries[0][0]
            author_entries = book.get_metadata('DC', 'creator')
            if author_entries:
                author = author_entries[0][0]
            description_entries = book.get_metadata('DC', 'description')
            if description_entries:
                description = description_entries[0][0]
        except Exception as e:
            logging.error(f"Error extracting EPUB metadata from {file_path}: {e}")
        return self.sanitize_text(title), self.sanitize_text(author), self.sanitize_text(description)

    def extract_pdf_metadata(self, file_path):
        try:
            reader = PdfReader(file_path)
            info = reader.metadata
            title = info.title if info.title else ""
            author = info.author if info.author else ""
            description = ""
            if reader.pages:
                first_page_text = reader.pages[0].extract_text() or ""
                description = first_page_text[:300]
            return self.sanitize_text(title), self.sanitize_text(author), self.sanitize_text(description)
        except Exception as e:
            error_msg = str(e)
            if "EOF marker" in error_msg:
                logging.error(
                    f"PDF file {file_path} appears to be corrupt (EOF marker not found). Skipping metadata extraction.")
            else:
                logging.error(f"Error extracting PDF metadata from {file_path}: {e}")
            # Return empty metadata to allow processing to continue.
            return "", "", ""

    def fetch_online_metadata(self, query):
        base_url = "https://openlibrary.org/search.json?q="
        url = base_url + quote(query)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("numFound", 0) > 0 and data.get("docs"):
                doc = data["docs"][0]
                metadata = {
                    "title": doc.get("title", ""),
                    "authors": ", ".join(doc.get("author_name", [])),
                    "publish_year": doc.get("first_publish_year", ""),
                    "isbn": doc.get("isbn", [None])[0] if doc.get("isbn") else None,
                    "subjects": ", ".join(doc.get("subject", []))
                }
                return metadata
            else:
                logging.warning(f"No results found for query: {query}")
                return None
        except Exception as e:
            logging.error(f"Error fetching metadata online for query '{query}': {e}")
            return None

    def extract_author_from_filename(self, file_path):
        if self.instruction_model is None:
            filename = self.sanitize_filename(os.path.splitext(os.path.basename(file_path))[0])
            parts = filename.split(" - ")
            if len(parts) > 1:
                return parts[0].strip()
            else:
                return "Unknown Author"
        filename = os.path.splitext(os.path.basename(file_path))[0]
        prompt = f"Extract the author name from the following book title: '{filename}'. If no author can be determined, return 'Unknown Author'."
        try:
            result = self.instruction_model(prompt)
            extracted_author = result[0]['generated_text'].strip()
            return extracted_author if extracted_author else "Unknown Author"
        except Exception as e:
            logging.error(f"Error extracting author from filename '{filename}': {e}")
            return "Unknown Author"

    def get_book_metadata(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == ".epub":
            title, author, description = self.extract_epub_metadata(file_path)
        elif file_ext == ".pdf":
            title, author, description = self.extract_pdf_metadata(file_path)
        else:
            title, author, description = "", "", ""
        if not author or len(author.strip()) < 3:
            author = self.extract_author_from_filename(file_path)
        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]
        return title, author, description
