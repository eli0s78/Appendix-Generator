"""
Session management for Appendix Generator.

Provides save/load functionality to persist and restore user progress.
"""

import json
import gzip
import base64
import re
from datetime import datetime
from io import BytesIO


def encode_api_key(key: str) -> str:
    """Basic obfuscation for API key (base64 encoding)."""
    if not key:
        return None
    return base64.b64encode(key.encode()).decode()


def decode_api_key(encoded: str) -> str:
    """Decode obfuscated API key."""
    if not encoded:
        return None
    try:
        return base64.b64decode(encoded.encode()).decode()
    except Exception:
        return None


def extract_book_title(session_state: dict) -> str:
    """Extract book title from planning data or return default."""
    planning = session_state.get("planning_data")
    if planning:
        overview = planning.get("book_overview", {})
        return overview.get("title", "Untitled")
    return "Untitled"


def get_session_filename(session_state: dict) -> str:
    """Generate filename for session save."""
    title = extract_book_title(session_state)
    # Sanitize for filename
    safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip()
    safe_title = re.sub(r'\s+', '_', safe_title) or "session"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{safe_title}_{timestamp}.appendix-session"


def save_session(session_state: dict) -> bytes:
    """Serialize session state to compressed JSON.

    Args:
        session_state: Dictionary containing session state values

    Returns:
        Gzip-compressed JSON bytes
    """
    data = {
        "version": "1.0",
        "app_name": "Appendix Generator",
        "saved_at": datetime.utcnow().isoformat() + "Z",
        "book_title": extract_book_title(session_state),

        # API key (base64 encoded for basic obfuscation)
        "api_key_encoded": encode_api_key(session_state.get("api_key")),

        # Core data
        "book_content": session_state.get("book_content"),
        "extraction_info": session_state.get("extraction_info"),
        "planning_data": session_state.get("planning_data"),
        "generated_appendices": session_state.get("generated_appendices", {}),
        "ready_to_generate": session_state.get("ready_to_generate", False),
        "working_model": session_state.get("working_model"),
    }

    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')

    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
        gz.write(json_bytes)

    return buffer.getvalue()


def load_session(file_bytes: bytes) -> dict:
    """Deserialize compressed JSON to session data.

    Args:
        file_bytes: Gzip-compressed JSON bytes

    Returns:
        Dictionary with session data

    Raises:
        ValueError: If file version is unsupported
    """
    buffer = BytesIO(file_bytes)

    with gzip.GzipFile(fileobj=buffer, mode='rb') as gz:
        json_bytes = gz.read()

    data = json.loads(json_bytes.decode('utf-8'))

    # Validate version
    if data.get("version") != "1.0":
        raise ValueError(f"Unsupported session version: {data.get('version')}")

    return data
