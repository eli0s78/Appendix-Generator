"""
LLM Client - Handles communication with Google Gemini API.
"""

import google.generativeai as genai
from typing import Optional
import json
import re


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


def call_gemini(prompt: str, model_name: str = "gemini-1.5-pro") -> str:
    """
    Send a prompt to Gemini and get a response.
    
    Args:
        prompt: The prompt to send
        model_name: Which Gemini model to use
        
    Returns:
        The model's response text
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        # Configure generation settings
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=8192,
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


def test_api_key(api_key: str) -> bool:
    """
    Test if the API key is valid by making a simple request.
    
    Args:
        api_key: Google AI Studio API key
        
    Returns:
        True if key is valid
    """
    try:
        configure_gemini(api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content("Say 'API key valid' and nothing else.")
        return "valid" in response.text.lower()
    except Exception:
        return False
