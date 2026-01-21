"""
LLM Client - Handles communication with Google Gemini API.
Uses the new google-genai SDK with Client object pattern.
"""

from google import genai
from google.genai import types
from typing import Tuple, List, Optional
import json
import re

# Module-level client storage
_client: Optional[genai.Client] = None


def get_client() -> Optional[genai.Client]:
    """Get the current Gemini client."""
    return _client


def configure_gemini(api_key: str) -> genai.Client:
    """
    Configure the Gemini API with the provided key.
    Returns a Client object for making API calls.
    """
    global _client
    try:
        _client = genai.Client(api_key=api_key)
        return _client
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


def find_best_model(api_key: str) -> Tuple[str, str]:
    """
    Find the best available Gemini model, prioritizing newer versions.
    Returns tuple of (model_id, display_name)
    """
    try:
        client = genai.Client(api_key=api_key)
        available = []
        
        for model in client.models.list():
            model_name = model.name if hasattr(model, 'name') else str(model)
            available.append(model_name)
    except Exception as e:
        return None, f"Cannot list models: {str(e)}"
    
    # Priority order - Gemini 3 Pro first, then Pro variants before Flash
    # Model names from API are like "models/gemini-2.0-flash"
    priority_patterns = [
        ("gemini-3-pro", "Gemini 3 Pro"),
        ("gemini-3.0-pro", "Gemini 3 Pro"),
        ("gemini-2.5-pro", "Gemini 2.5 Pro"),
        ("gemini-2.0-pro", "Gemini 2.0 Pro"),
        ("gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("gemini-2.0-flash", "Gemini 2.0 Flash"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ("gemini-pro", "Gemini Pro"),
    ]
    
    for pattern, display_name in priority_patterns:
        for model_name in available:
            if pattern in model_name.lower():
                # Extract just the model ID (remove "models/" prefix)
                model_id = model_name.replace("models/", "")
                return model_id, f"{display_name} ({model_id})"
    
    # If nothing matched, return first available
    if available:
        model_id = available[0].replace("models/", "")
        return model_id, f"Available model ({model_id})"
    
    return None, "No models available"


def call_gemini(prompt: str, model_name: str = None, client: genai.Client = None) -> str:
    """
    Send a prompt to Gemini and get a response.
    Uses the global client if none is provided.
    """
    if client is None:
        client = _client
    
    if client is None:
        raise Exception("Gemini client not configured. Please set your API key first.")
    
    if model_name is None:
        model_name = "gemini-2.0-flash"  # Safe fallback
    
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
        error_msg = str(e).lower()
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


def test_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if the API key is valid and find the best available model.
    """
    api_key = api_key.strip()
    
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith("AIza"):
        return False, "API key should start with 'AIza'. Please check you copied the full key from Google AI Studio."
    
    try:
        # Create a client with the API key
        client = genai.Client(api_key=api_key)
        
        # Find the best model
        model_id, model_display = find_best_model(api_key)
        
        if model_id is None:
            # List what we found for debugging
            available = list_available_models(api_key)
            return False, f"No compatible models found. Available: {', '.join(available[:5])}"
        
        # Test the model with a simple generation
        try:
            response = client.models.generate_content(
                model=model_id,
                contents="Say OK"
            )
            if response and response.text:
                return True, f"API key valid! Using: {model_display}"
        except Exception as e:
            return False, f"Model {model_id} failed: {str(e)}"
        
        return False, "Could not validate any model"
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "api_key" in error_msg or "invalid" in error_msg:
            return False, "Invalid API key. Please get a new key from Google AI Studio."
        elif "quota" in error_msg:
            return False, "API quota exceeded. Please wait or check your usage limits."
        else:
            return False, f"Error: {str(e)}"


def get_working_model(api_key: str) -> str:
    """
    Get the best working model ID.
    """
    model_id, _ = find_best_model(api_key)
    return model_id if model_id else "gemini-2.0-flash"
