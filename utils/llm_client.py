"""
LLM Client - Handles communication with Google Gemini API.
Uses the new google-genai SDK with Client object pattern.

IMPORTANT: This module is STATELESS to support multiple concurrent users.
Each function creates its own client using the provided API key.
Tier detection results should be stored in Streamlit session_state, not here.
"""

from google import genai
from google.genai import types
from typing import Tuple, List, Optional
import json
import re


def get_detected_tier() -> Optional[str]:
    """
    DEPRECATED: Tier should be stored in session_state, not globally.
    This function exists for backward compatibility but always returns None.
    Use st.session_state.detected_tier instead.
    """
    return None


def detect_api_tier(api_key: str) -> str:
    """
    Detect whether the API key is on free or paid tier.

    Strategy: Try Pro model directly (synchronous, no threads).
    - Free tier keys fail INSTANTLY with quota error (limit: 0)
    - Paid tier keys succeed (may take a few seconds)

    Returns: "paid" or "free"

    NOTE: Result should be stored in session_state by the caller.
    NOTE: This is now synchronous to avoid daemon thread instability.
    """
    try:
        client = genai.Client(api_key=api_key)
        # Use Pro model - free tier fails instantly, paid tier works
        client.models.generate_content(
            model="gemini-2.5-pro",
            contents="OK"
        )
        # If we get here, Pro worked - paid tier confirmed
        return "paid"
    except Exception as e:
        error_str = str(e)
        error_lower = error_str.lower()

        # Check if it's a free tier quota error
        is_free_tier = any([
            "free_tier" in error_lower,
            "limit: 0" in error_str,
            "limit\":0" in error_str,
            "limit\": 0" in error_str,
            ("resource_exhausted" in error_lower and "limit" in error_lower),
            ("quota" in error_lower and "pro" in error_lower),
        ])

        if is_free_tier:
            return "free"
        else:
            # Other errors (404, network, etc.) - default to free for safety
            return "free"


def configure_gemini(api_key: str) -> genai.Client:
    """
    Create a Gemini client with the provided key.
    Returns a Client object for making API calls.

    NOTE: This creates a NEW client each time. For multi-user support,
    each user's API key should be stored in session_state.
    """
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to configure Gemini API: {str(e)}")


def list_available_models(api_key: str) -> List[str]:
    """
    List all available models for the given API key.
    """
    try:
        client = genai.Client(api_key=api_key)
        models = []
        for model in client.models.list():
            # Check if model supports generateContent
            if hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    models.append(model.name)
            else:
                # Include model if we can't check (assume it works)
                models.append(model.name)
        return models
    except Exception as e:
        return [f"Error listing models: {str(e)}"]


def find_best_model(api_key: str, tier: str = None) -> Tuple[str, str]:
    """
    Find the best available Gemini model based on API tier.
    Selects appropriate models based on tier.
    Returns tuple of (model_id, display_name)

    Args:
        api_key: Google API key
        tier: "paid" or "free" - should be passed from session_state

    NOTE: This function is kept for backward compatibility but is not used
    by the main app. Use get_working_model() instead for simpler model selection.
    """
    try:
        client = genai.Client(api_key=api_key)
        available = []

        for model in client.models.list():
            model_name = model.name if hasattr(model, 'name') else str(model)
            available.append(model_name)
    except Exception as e:
        return None, f"Cannot list models: {str(e)}"

    # Model names from API are like "models/gemini-2.0-flash"
    if tier == "paid":
        # Paid tier - use Gemini 3 Pro (preview) first, then Flash fallbacks
        priority_patterns = [
            ("gemini-3-pro-preview", "Gemini 3 Pro Preview"),  # Best for paid users
            ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            ("gemini-2.5-flash", "Gemini 2.5 Flash"),  # Fallback
            ("gemini-2.0-flash", "Gemini 2.0 Flash"),
        ]
    else:
        # Free tier - only stable Flash models work reliably
        # Preview models appear in list but may not be accessible
        priority_patterns = [
            ("gemini-2.5-flash", "Gemini 2.5 Flash"),
            ("gemini-2.0-flash", "Gemini 2.0 Flash"),
            ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ]

    for pattern, display_name in priority_patterns:
        for model_name in available:
            if pattern in model_name.lower():
                # Extract just the model ID (remove "models/" prefix)
                model_id = model_name.replace("models/", "")
                tier_label = " [Paid]" if tier == "paid" else " [Free]"
                return model_id, f"{display_name} ({model_id}){tier_label}"

    # If nothing matched, return first available
    if available:
        model_id = available[0].replace("models/", "")
        return model_id, f"Available model ({model_id})"

    return None, "No models available"


def _is_free_tier_error(error_str: str) -> bool:
    """Check if an error indicates free tier quota limit."""
    error_lower = error_str.lower()
    return any([
        "free_tier" in error_lower,
        "limit: 0" in error_str,
        "limit\":0" in error_str,
        "limit\": 0" in error_str,
        ("resource_exhausted" in error_lower and "limit" in error_lower),
    ])


def call_gemini(prompt: str, model_name: str = None, api_key: str = None, client: genai.Client = None) -> str:
    """
    Send a prompt to Gemini and get a response.

    Args:
        prompt: The prompt to send
        model_name: Model to use (default: gemini-2.5-flash)
        api_key: API key to create a fresh client (recommended for multi-user)
        client: Pre-created client (legacy, not recommended)

    Includes automatic fallback: if a Pro model fails with quota errors
    (indicating free tier), automatically retries with Flash model.
    """
    # Create a fresh client for this request if api_key provided
    if api_key:
        client = genai.Client(api_key=api_key)

    if client is None:
        raise Exception("Gemini client not configured. Please provide an API key.")

    if model_name is None:
        model_name = "gemini-2.5-flash"  # Use stable Flash as fallback

    # Track if we should try fallback on Pro model failure
    is_pro_model = "pro" in model_name.lower()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=16384,
            )
        )

        # Handle different response structures in new SDK
        if response is None:
            raise Exception("Empty response from AI")

        # Try to get text from response
        if hasattr(response, 'text') and response.text:
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Fallback: extract from candidates
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    return candidate.content.parts[0].text

        # If we get here, try converting to string
        return str(response)

    except Exception as e:
        error_str = str(e)
        error_msg = error_str.lower()

        # Check if this is a free tier error on a Pro model
        # If so, retry with Flash model
        if is_pro_model and _is_free_tier_error(error_str):
            fallback_model = "gemini-2.5-flash"  # Use stable Flash
            try:
                response = client.models.generate_content(
                    model=fallback_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=16384,
                    )
                )
                if response and hasattr(response, 'text') and response.text:
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            return candidate.content.parts[0].text
                return str(response)
            except Exception as fallback_error:
                raise Exception(f"⚠️ AI service error: {str(fallback_error)}\n\n💡 Try again in a moment.")

        # Standard error handling
        if "quota" in error_msg or "rate" in error_msg:
            raise Exception("⚠️ API quota exceeded. Please wait a few minutes and try again, or check your API quota at https://aistudio.google.com/")
        elif "invalid" in error_msg and "key" in error_msg:
            raise Exception("❌ Invalid API key. Please check your API key in the sidebar and try again.")
        elif "not found" in error_msg or "404" in error_msg:
            raise Exception(f"⚠️ Model '{model_name}' not available. The app will try to use a different model automatically.")
        elif "network" in error_msg or "connection" in error_msg:
            raise Exception("🌐 Network error. Please check your internet connection and try again.")
        else:
            raise Exception(f"⚠️ AI service error: {str(e)}\n\n💡 Try again in a moment. If the problem persists, check your API key.")


def parse_json_response(response: str) -> dict:
    """
    Parse JSON from Gemini's response, handling markdown code blocks.
    """
    if not response:
        raise Exception("⚠️ Empty response from AI.\n\n💡 Please try again.")
    
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_obj_match = re.search(r'\{[\s\S]*\}', response)
        if json_obj_match:
            json_str = json_obj_match.group(0)
        else:
            json_str = response.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try cleaning up common issues
        json_str = json_str.replace('\n', ' ')
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Include first 500 chars of response for debugging
            preview = response[:500] if len(response) > 500 else response
            raise Exception(f"⚠️ Unexpected response format from AI.\n\n💡 The AI returned data in an unexpected format. Please try again - this usually resolves itself on retry.\n\nDebug (first 500 chars): {preview}")


def test_api_key(api_key: str) -> Tuple[bool, str, Optional[str]]:
    """
    Test if the API key is valid and detect tier.

    OPTIMIZED: Makes 2 API calls total (validation + tier detection).

    Returns:
        Tuple of (success, message, detected_tier)
        - success: True if API key is valid
        - message: Status message for display
        - detected_tier: "paid" or "free" (None if validation failed)

    The caller should store detected_tier in session_state for multi-user support.
    """
    api_key = api_key.strip()

    if not api_key:
        return False, "API key is empty", None

    if not api_key.startswith("AIza"):
        return False, "API key should start with 'AIza'. Please check you copied the full key from Google AI Studio.", None

    try:
        # Create a client with the API key
        client = genai.Client(api_key=api_key)

        # Validate with Flash model (works for all tiers)
        validation_model = "gemini-2.5-flash"

        try:
            response = client.models.generate_content(
                model=validation_model,
                contents="OK"
            )
            if response and response.text:
                # Key is valid - now detect tier (runs in background, quick for paid tier)
                detected = detect_api_tier(api_key)

                # Select model based on tier
                if detected == "paid":
                    model_name = "Gemini 3 Pro (Preview)"
                else:
                    model_name = "Gemini 2.5 Flash"

                tier_label = "Paid" if detected == "paid" else "Free"
                return True, f"API key valid! Using: {model_name} [{tier_label}]", detected
        except Exception as e:
            error_str = str(e)
            error_lower = error_str.lower()

            # Check if it's a quota/tier issue
            if "quota" in error_lower or "resource_exhausted" in error_lower:
                return False, "API quota exceeded. Please wait or check your usage limits.", None
            elif "invalid" in error_lower and "key" in error_lower:
                return False, "Invalid API key. Please get a new key from Google AI Studio.", None
            else:
                return False, f"Validation failed: {str(e)}", None

        return False, "Could not validate the API key", None

    except Exception as e:
        error_msg = str(e).lower()

        if "api_key" in error_msg or "invalid" in error_msg:
            return False, "Invalid API key. Please get a new key from Google AI Studio.", None
        elif "quota" in error_msg:
            return False, "API quota exceeded. Please wait or check your usage limits.", None
        else:
            return False, f"Error: {str(e)}", None


def get_working_model(api_key: str = None, tier: str = None) -> str:
    """
    Get the best working model ID based on tier.

    Args:
        api_key: Unused, kept for backward compatibility
        tier: "paid" or "free" - should be passed from session_state

    Returns model ID based on tier.
    """
    if tier == "paid":
        return "gemini-3-pro-preview"
    else:
        return "gemini-2.5-flash"
