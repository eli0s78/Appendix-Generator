"""
LLM Client - Handles communication with Google Gemini API.
Uses Gemini 3 Pro as the primary model.
"""

import google.generativeai as genai
from typing import Tuple
import json
import re

# Default model - Gemini 3 Pro (latest flagship model)
DEFAULT_MODEL = "gemini-3.0-pro"


def configure_gemini(api_key: str) -> bool:
    """
    Configure the Gemini API with the provided key.
    
    Args:
        api_key: Google AI Studio API key
        
    Returns:
        True if configuration successful
    """
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        raise Exception(f"Failed to configure Gemini API: {str(e)}")


def call_gemini(prompt: str, model_name: str = DEFAULT_MODEL) -> str:
    """
    Send a prompt to Gemini and get a response.
    
    Args:
        prompt: The prompt to send
        model_name: Which Gemini model to use (default: Gemini 3 Pro)
        
    Returns:
        The model's response text
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        # Configure generation settings
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=16384,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def parse_json_response(response: str) -> dict:
    """
    Parse JSON from Gemini's response, handling markdown code blocks.
    
    Args:
        response: Raw response text from Gemini
        
    Returns:
        Parsed JSON as dictionary
    """
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try parsing the whole response
        json_str = response.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try to fix common issues
        json_str = json_str.replace('\n', ' ')
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON response: {str(e)}\n\nResponse was:\n{response[:500]}...")


def test_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if the API key is valid by making a simple request.
    
    Args:
        api_key: Google AI Studio API key
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Clean the API key (remove any accidental whitespace)
    api_key = api_key.strip()
    
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith("AIza"):
        return False, "API key should start with 'AIza'. Please check you copied the full key from Google AI Studio."
    
    try:
        genai.configure(api_key=api_key)
        
        # Models to try - Gemini 3 Pro first, then fallbacks
        models_to_try = [
            ("gemini-3.0-pro", "Gemini 3 Pro"),
            ("gemini-3.0-flash", "Gemini 3 Flash"),
            ("gemini-2.5-pro-preview-05-06", "Gemini 2.5 Pro"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ]
        
        last_error = None
        for model_id, model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_id)
                response = model.generate_content("Say OK")
                if response and response.text:
                    return True, f"API key valid! Using: {model_name}"
            except Exception as e:
                last_error = str(e)
                continue
        
        return False, f"API key seems valid but no models available. Error: {last_error}"
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "api_key" in error_msg or "invalid" in error_msg:
            return False, "Invalid API key. Please get a new key from Google AI Studio."
        elif "quota" in error_msg:
            return False, "API quota exceeded. Please wait or check your Google AI Studio usage limits."
        elif "permission" in error_msg:
            return False, "Permission denied. Make sure the API is enabled in your Google AI Studio account."
        else:
            return False, f"Error: {str(e)}"


def get_working_model(api_key: str) -> str:
    """
    Find the best available model for the given API key.
    Prioritizes Gemini 3 Pro.
    
    Args:
        api_key: Google AI Studio API key
        
    Returns:
        Model identifier string
    """
    genai.configure(api_key=api_key)
    
    models_to_try = [
        "gemini-3.0-pro",
        "gemini-3.0-flash",
        "gemini-2.5-pro-preview-05-06",
        "gemini-1.5-pro",
    ]
    
    for model_id in models_to_try:
        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content("Test")
            if response and response.text:
                return model_id
        except Exception:
            continue
    
    return DEFAULT_MODEL  # Return default even if test failed
