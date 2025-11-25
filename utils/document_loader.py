import PyPDF2
from config import MAX_CHUNK_SIZE, CHUNK_OVERLAP


def load_pdf(file_path: str) -> str:

    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return ""


def load_txt(file_path: str) -> str:

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading TXT: {e}")
        return ""


def chunk_text(text, chunk_size = MAX_CHUNK_SIZE, overlap= CHUNK_OVERLAP):

    chunks = []

    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def process_document(file_path: str, file_type: str) -> list:
    if file_type.lower() == 'pdf':
        text = load_pdf(file_path)

    elif file_type.lower() == 'txt':
        text = load_txt(file_path)

    else:
        return []
    
    if not text:
        return []
    
    return chunk_text(text)