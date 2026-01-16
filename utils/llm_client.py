"""
LLM Client - Handles communication with Google Gemini API.
Uses Gemini 3 Pro as the primary model.
"""

import google.generativeai as genai
from typing import Tuple, List
import json
import re


def configure_gemini(api_key: str) -> bool:
    """
    Configure the Gemini API with the provided key.
    """
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        raise Exception(f"Failed to configure Gemini API: {str(e)}")


def list_available_models(api_key: str) -> List[str]:
    """
    List all available models for the given API key.
    """
    try:
        genai.configure(api_key=api_key)
        models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                models.append(model.name)
        return models
    except Exception as e:
        return [f"Error listing models: {str(e)}"]


def find_best_model(api_key: str) -> Tuple[str, str]:
    """
    Find the best available Gemini model, prioritizing Gemini 3.
    Returns tuple of (model_id, display_name)
    """
    genai.configure(api_key=api_key)
    
    # Get all available models
    available = []
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                available.append(model.name)
    except Exception as e:
        return None, f"Cannot list models: {str(e)}"
    
    # Priority order - look for Gemini 3 first, then 2.5, then 2.0, then 1.5
    # Model names from API are like "models/gemini-3.0-pro"
    priority_patterns = [
        ("gemini-3", "Gemini 3"),
        ("gemini-2.5", "Gemini 2.5"),
        ("gemini-2.0", "Gemini 2.0"),
        ("gemini-2", "Gemini 2"),
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


def call_gemini(prompt: str, model_name: str = None) -> str:
    """
    Send a prompt to Gemini and get a response.
    """
    if model_name is None:
        model_name = "gemini-1.5-flash"  # Safe fallback
    
    try:
        model = genai.GenerativeModel(model_name)
        
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
    """
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        json_str = json_str.replace('\n', ' ')
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON: {str(e)}\n\nResponse was:\n{response[:500]}...")


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
        genai.configure(api_key=api_key)
        
        # Find the best model
        model_id, model_display = find_best_model(api_key)
        
        if model_id is None:
            # List what we found for debugging
            available = list_available_models(api_key)
            return False, f"No compatible models found. Available: {', '.join(available[:5])}"
        
        # Test the model
        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content("Say OK")
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
    genai.configure(api_key=api_key)
    model_id, _ = find_best_model(api_key)
    return model_id if model_id else "gemini-1.5-flash"
