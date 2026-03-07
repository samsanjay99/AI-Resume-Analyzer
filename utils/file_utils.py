"""
File utility functions for resume processing
"""
import pypdf as PyPDF2
import io
from docx import Document
import tempfile
import os

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        # Create a PDF reader object
        if hasattr(uploaded_file, 'read'):
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
        else:
            file_content = uploaded_file
            
        # Create BytesIO from bytes content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    try:
        # Save uploaded file to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            if hasattr(uploaded_file, 'getbuffer'):
                temp_file.write(uploaded_file.getbuffer())
            else:
                temp_file.write(uploaded_file.read())
                uploaded_file.seek(0)
            temp_path = temp_file.name
        
        # Extract text using python-docx
        doc = Document(temp_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    try:
        if hasattr(uploaded_file, 'getvalue'):
            return uploaded_file.getvalue().decode('utf-8')
        elif hasattr(uploaded_file, 'read'):
            content = uploaded_file.read()
            if isinstance(content, bytes):
                return content.decode('utf-8')
            return content
        else:
            return str(uploaded_file)
    except Exception as e:
        raise Exception(f"Error extracting text from TXT: {str(e)}")