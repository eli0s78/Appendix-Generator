"""
PDF Handler - Extracts text content from uploaded PDF files.
Optimized for large academic books (100-600+ pages).
"""

import pdfplumber
from typing import Tuple
import io


def validate_pdf_file(pdf_file) -> Tuple[bool, str]:
    """
    Validate PDF file before processing.

    Args:
        pdf_file: Uploaded file object from Streamlit

    Returns:
        Tuple of (is_valid, message)
    """
    # Check file size (50MB limit for smooth processing)
    file_size_mb = pdf_file.size / (1024 * 1024)

    if file_size_mb > 100:
        return False, f"⚠️ File is very large ({file_size_mb:.1f} MB). For best results, use PDFs under 100MB. Large files may take several minutes to process."

    if file_size_mb > 50:
        return True, f"ℹ️ Large file detected ({file_size_mb:.1f} MB). Processing may take a few minutes."

    return True, "✓ File size OK"


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
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise Exception("🔒 This PDF is password-protected. Please use an unprotected PDF file.")
        elif "corrupt" in error_msg or "damaged" in error_msg:
            raise Exception("⚠️ This PDF file appears to be corrupted. Please try a different file or re-download the PDF.")
        else:
            raise Exception(f"⚠️ Could not read PDF file: {str(e)}\n\n💡 Make sure the file is a valid PDF document.")
    
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
        "estimated_words": 0,
        "estimated_chars": 0
    }
    
    try:
        pdf_file.seek(0)
        
        with pdfplumber.open(pdf_file) as pdf:
            info["pages"] = len(pdf.pages)
            
            # Sample more pages for better estimate
            sample_pages = min(10, info["pages"])
            sample_text = ""
            for i in range(sample_pages):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    sample_text += text
            
            if sample_text:
                chars_per_page = len(sample_text) / sample_pages
                words_per_page = len(sample_text.split()) / sample_pages
                
                info["has_text"] = True
                info["estimated_chars"] = int(chars_per_page * info["pages"])
                info["estimated_words"] = int(words_per_page * info["pages"])
                    
    except Exception as e:
        info["error"] = str(e)
        
    pdf_file.seek(0)
    
    return info


def truncate_content_smart(content: str, max_chars: int = 900000) -> Tuple[str, dict]:
    """
    Smart truncation that preserves beginning and end of the book.
    This ensures we capture both the table of contents (usually at the start)
    and the later chapters (at the end).
    
    Args:
        content: The text content
        max_chars: Maximum characters to keep (default ~225k words, enough for most books)
        
    Returns:
        Tuple of (truncated_content, truncation_info)
    """
    truncation_info = {
        "was_truncated": False,
        "original_chars": len(content),
        "final_chars": len(content),
        "kept_percentage": 100
    }
    
    if len(content) <= max_chars:
        return content, truncation_info
    
    # We need to truncate
    truncation_info["was_truncated"] = True
    
    # Strategy: Keep 60% from beginning (includes TOC, early chapters) 
    # and 40% from end (includes later chapters)
    beginning_chars = int(max_chars * 0.6)
    end_chars = int(max_chars * 0.4)
    
    # Get beginning portion
    beginning = content[:beginning_chars]
    # Try to end at a page break
    last_page_break = beginning.rfind("[Page ")
    if last_page_break > beginning_chars * 0.8:
        beginning = beginning[:last_page_break]
    
    # Get ending portion
    ending = content[-end_chars:]
    # Try to start at a page break
    first_page_break = ending.find("[Page ")
    if first_page_break != -1 and first_page_break < end_chars * 0.2:
        ending = ending[first_page_break:]
    
    # Combine with clear marker
    truncated = (
        beginning + 
        "\n\n[... CONTENT TRUNCATED FOR LENGTH - MIDDLE SECTION OMITTED ...]\n\n" +
        ending
    )
    
    truncation_info["final_chars"] = len(truncated)
    truncation_info["kept_percentage"] = round((len(truncated) / len(content)) * 100, 1)
    
    return truncated, truncation_info


def truncate_content(content: str, max_chars: int = 900000) -> str:
    """
    Wrapper for backward compatibility.
    Uses smart truncation internally.
    """
    truncated, _ = truncate_content_smart(content, max_chars)
    return truncated


def extract_with_info(pdf_file) -> Tuple[str, dict]:
    """
    Extract text from PDF and return both content and extraction info.
    
    Args:
        pdf_file: Uploaded file object from Streamlit
        
    Returns:
        Tuple of (text_content, extraction_info)
    """
    pdf_file.seek(0)
    
    # Get PDF info first
    pdf_info = get_pdf_info(pdf_file)
    pdf_file.seek(0)
    
    # Extract full text
    full_text = extract_text_from_pdf(pdf_file)
    
    # Apply smart truncation
    truncated_text, truncation_info = truncate_content_smart(full_text)
    
    # Combine info
    extraction_info = {
        **pdf_info,
        **truncation_info
    }
    
    return truncated_text, extraction_info
