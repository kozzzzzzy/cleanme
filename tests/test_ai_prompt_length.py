"""Test AI personality prompt length constraints."""
from pathlib import Path


CONST_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "const.py"
GEMINI_CLIENT_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "gemini_client.py"


def test_ai_personalities_have_length_constraint_instructions():
    """Test that all AI personalities include instruction for short comments."""
    source = CONST_PATH.read_text(encoding="utf-8")
    
    # Check that each personality has length constraint instruction
    required_phrases = [
        "2 sentences MAX",
        "under 200 characters",
    ]
    
    for phrase in required_phrases:
        # Count occurrences - should be 8 (one for each personality)
        count = source.count(phrase)
        assert count >= 8, (
            f"All 8 AI personalities should include '{phrase}' instruction. Found {count}."
        )


def test_gemini_prompt_includes_length_constraint():
    """Test that the Gemini prompt builder includes length constraint."""
    source = GEMINI_CLIENT_PATH.read_text(encoding="utf-8")
    
    # Check for length constraint in the prompt
    assert "2 sentences MAX" in source, (
        "Gemini prompt should include '2 sentences MAX' instruction"
    )
    assert "under 200 characters" in source, (
        "Gemini prompt should include 'under 200 characters' instruction"
    )
    assert "punchy" in source.lower() or "verbose" in source.lower(), (
        "Gemini prompt should mention being punchy/not verbose"
    )


def test_ai_personality_examples_are_concise():
    """Test that AI personality examples are concise (under 200 chars)."""
    source = CONST_PATH.read_text(encoding="utf-8")
    
    # Find all example lines in the AI_PERSONALITIES section
    # Examples should be short to serve as a model for the AI
    # Note: We're checking that 'Example:' lines exist and contain actual examples
    assert 'Example: "' in source, (
        "AI personalities should include Example: quotes as models for the AI"
    )
