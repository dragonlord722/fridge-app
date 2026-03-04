import pytest
import os
from app.main import load_prompt

def test_load_prompt_success():
    """Verify the loader can read the v2_guardrail.md file."""
    # This assumes you have created backend/prompts/v2_guardrail.md
    content = load_prompt("v2_guardrail")
    assert "is_valid_fridge_image" in content
    assert "JSON" in content

def test_load_prompt_fallback():
    """Verify the loader returns a fallback string if the file is missing."""
    content = load_prompt("non_existent_version")
    assert "Using fallback" in content or "Analyze this fridge" in content

def test_prompt_directory_structure():
    """Verify the prompts directory exists in the expected location."""
    base_path = os.path.dirname(os.path.dirname(__file__))
    prompt_dir = os.path.join(base_path, "prompts")
    assert os.path.isdir(prompt_dir)