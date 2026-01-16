"""
PDF Handler - Extracts text content from uploaded PDF files.
"""

import pdfplumber
from typing import Optional
import io


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: Uploaded file object from Streamlit
        
    Returns:
        Extracted text as a string
    """
    text_content = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"[Page {i+1}]\n{page_text}")
                    
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")
    
    return "\n\n".join(text_content)


def get_pdf_info(pdf_file) -> dict:
    """
    Get basic information about a PDF file.
    
    Args:
        pdf_file: Uploaded file object from Streamlit
        
    Returns:
        Dictionary with PDF metadata
    """
    info = {
        "pages": 0,
        "has_text": False,
        "estimated_words": 0
    }
    
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        with pdfplumber.open(pdf_file) as pdf:
            info["pages"] = len(pdf.pages)
            
            # Check first few pages for text
            sample_text = ""
            for page in pdf.pages[:5]:
                text = page.extract_text()
                if text:
                    sample_text += text
                    
            info["has_text"] = len(sample_text) > 100
            info["estimated_words"] = len(sample_text.split()) * (info["pages"] / min(5, info["pages"]))
            
    except Exception as e:
        info["error"] = str(e)
        
    # Reset file pointer for subsequent use
    pdf_file.seek(0)
    
    return info


def truncate_content(content: str, max_chars: int = 500000) -> str:
    """
    Truncate content if it exceeds maximum character limit.
    Gemini has token limits, so we may need to truncate very long books.
    
    Args:
        content: The text content
        max_chars: Maximum characters to keep
        
    Returns:
        Truncated content with note if truncated
    """
    if len(content) <= max_chars:
        return content
    
    truncated = content[:max_chars]
    
    # Try to end at a paragraph break
    last_break = truncated.rfind("\n\n")
    if last_break > max_chars * 0.8:
        truncated = truncated[:last_break]
    
    truncated += "\n\n[NOTE: Content truncated due to length. Analysis based on first portion of the book.]"
    
    return truncated
