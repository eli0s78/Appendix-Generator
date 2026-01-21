"""
PDF Handler - Extracts text content from uploaded PDF files.
Optimized for large academic books (100-600+ pages).
Includes smart filtering of bibliography and index sections.
"""

import pdfplumber
from typing import Tuple
import io
import re


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


def detect_and_remove_bibliography(content: str) -> Tuple[str, dict]:
    """
    Detect and remove bibliography/references sections from book content.
    These sections are not needed for appendix generation and can save significant tokens.
    
    Args:
        content: The full text content of the book
        
    Returns:
        Tuple of (cleaned_content, removal_info)
    """
    removal_info = {
        "bibliography_removed": False,
        "bibliography_chars_saved": 0,
        "sections_found": []
    }
    
    original_length = len(content)
    
    # Common bibliography/references section headers (case-insensitive)
    # These patterns look for section headers that typically start bibliography sections
    bib_header_patterns = [
        # Standard headers with page markers
        r'\[Page \d+\]\s*\n?\s*(References|Bibliography|Works Cited|Literature Cited|Sources|Cited Works|Reference List|Works Referenced)\s*\n',
        # Headers at start of line
        r'\n\s*(References|Bibliography|Works Cited|Literature Cited|Cited Works|Reference List)\s*\n',
        # Numbered chapter-style headers
        r'\n\s*(?:Chapter\s+)?\d*\.?\s*(References|Bibliography)\s*\n',
    ]
    
    # Find the earliest bibliography section start
    bib_start = None
    bib_section_name = None
    
    for pattern in bib_header_patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in matches:
            # Only consider matches in the last 40% of the document
            # (bibliographies are typically at the end)
            if match.start() > len(content) * 0.6:
                if bib_start is None or match.start() < bib_start:
                    bib_start = match.start()
                    bib_section_name = match.group(1) if match.lastindex else "References"
    
    if bib_start is not None:
        # Look for the next major section after bibliography that we should keep
        # (like Appendix, Index, or end of document)
        remaining_content = content[bib_start:]
        
        # Check if there's an appendix or other important section after bibliography
        next_section_patterns = [
            r'\[Page \d+\]\s*\n?\s*(Appendix|Appendices)\s',
            r'\n\s*(Appendix|Appendices)\s+[A-Z0-9]',
        ]
        
        next_section_start = None
        for pattern in next_section_patterns:
            match = re.search(pattern, remaining_content, re.IGNORECASE)
            if match:
                # Found an appendix section - keep everything from there
                if next_section_start is None or match.start() < next_section_start:
                    next_section_start = match.start()
        
        if next_section_start is not None:
            # Remove only the bibliography section, keep the appendix
            content = content[:bib_start] + remaining_content[next_section_start:]
        else:
            # No appendix found, check for index section to also remove
            # Remove from bibliography to the end (or to index)
            content = content[:bib_start]
        
        removal_info["bibliography_removed"] = True
        removal_info["bibliography_chars_saved"] = original_length - len(content)
        removal_info["sections_found"].append(bib_section_name)
    
    return content, removal_info


def detect_and_remove_index(content: str) -> Tuple[str, dict]:
    """
    Detect and remove index sections from book content.
    Index sections are not needed for appendix generation.
    
    Args:
        content: The text content
        
    Returns:
        Tuple of (cleaned_content, removal_info)
    """
    removal_info = {
        "index_removed": False,
        "index_chars_saved": 0
    }
    
    original_length = len(content)
    
    # Index section patterns (typically at the very end)
    index_patterns = [
        r'\[Page \d+\]\s*\n?\s*(Subject Index|Author Index|Index|Name Index|General Index)\s*\n',
        r'\n\s*(Subject Index|Author Index|Index|Name Index|General Index)\s*\n',
    ]
    
    # Find index section in the last 20% of the document
    index_start = None
    
    for pattern in index_patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in matches:
            # Only consider matches in the last 20% (indexes are at the very end)
            if match.start() > len(content) * 0.8:
                if index_start is None or match.start() < index_start:
                    index_start = match.start()
    
    if index_start is not None:
        content = content[:index_start]
        removal_info["index_removed"] = True
        removal_info["index_chars_saved"] = original_length - len(content)
    
    return content, removal_info


def truncate_content_smart(content: str, max_chars: int = 1800000) -> Tuple[str, dict]:
    """
    Smart truncation that preserves beginning and end of the book.
    This ensures we capture both the table of contents (usually at the start)
    and the later chapters (at the end).
    
    Increased limit to 1.8M chars to support Gemini 2.x's larger context window.
    
    Args:
        content: The text content
        max_chars: Maximum characters to keep (default ~450k words)
        
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
    
    # Strategy: Keep 55% from beginning (includes TOC, intro, early chapters) 
    # and 45% from end (includes later chapters, conclusion)
    beginning_chars = int(max_chars * 0.55)
    end_chars = int(max_chars * 0.45)
    
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
    truncation_info["kept_percentage"] = round((len(truncated) / truncation_info["original_chars"]) * 100, 1)
    
    return truncated, truncation_info


def truncate_content(content: str, max_chars: int = 1800000) -> str:
    """
    Wrapper for backward compatibility.
    Uses smart truncation internally.
    """
    truncated, _ = truncate_content_smart(content, max_chars)
    return truncated


def extract_with_info(pdf_file) -> Tuple[str, dict]:
    """
    Extract text from PDF with smart filtering and return both content and extraction info.
    
    Processing pipeline:
    1. Extract full text from PDF
    2. Remove bibliography/references sections (not needed for appendix)
    3. Remove index sections (not needed for appendix)
    4. Apply smart truncation if still over limit
    
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
    original_chars = len(full_text)
    
    # Step 1: Remove bibliography/references sections
    cleaned_text, bib_info = detect_and_remove_bibliography(full_text)
    
    # Step 2: Remove index sections
    cleaned_text, index_info = detect_and_remove_index(cleaned_text)
    
    # Step 3: Apply smart truncation if still needed
    truncated_text, truncation_info = truncate_content_smart(cleaned_text)
    
    # Calculate total savings from filtering
    total_filtered_chars = bib_info["bibliography_chars_saved"] + index_info["index_chars_saved"]
    
    # Combine all info
    extraction_info = {
        **pdf_info,
        **truncation_info,
        "original_chars_before_filtering": original_chars,
        "bibliography_removed": bib_info["bibliography_removed"],
        "bibliography_chars_saved": bib_info["bibliography_chars_saved"],
        "index_removed": index_info["index_removed"],
        "index_chars_saved": index_info["index_chars_saved"],
        "total_filtered_chars": total_filtered_chars,
        "sections_removed": bib_info.get("sections_found", [])
    }
    
    return truncated_text, extraction_info
