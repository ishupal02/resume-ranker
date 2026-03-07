import PyPDF2
import os

def extract_text_from_pdf(file):
    """
    Reads a PDF file and extracts the text content.
    Returns the text as a string.
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_txt(file):
    """
    Reads a TXT file and extracts the text content.
    Returns the text as a string.
    """
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def get_candidate_name(file):
    """
    Extracts the candidate name from the filename.
    """
    filename = os.path.basename(file.name)
    name = os.path.splitext(filename)[0]
    return name.replace('_', ' ')