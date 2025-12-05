#!/usr/bin/env python3
"""
Unit tests for quote card generation functionality.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from analyze_quote import (
    create_fallback_analysis,
)
from generate_quote_card import QuoteCard


class TestFallbackAnalysis:
    """Tests for fallback quote analysis."""
    
    def test_fallback_has_required_fields(self):
        """Test that fallback analysis contains all required fields."""
        analysis = create_fallback_analysis("Test quote", "Test Author")
        
        assert "sentiment" in analysis
        assert "tone" in analysis
        assert "theme" in analysis
        assert "color_profile" in analysis
        assert "style_keywords" in analysis
        assert "fallback" in analysis
        assert analysis["fallback"] is True
    
    def test_fallback_uses_valid_color_profile(self):
        """Test that fallback uses a valid color profile."""
        analysis = create_fallback_analysis("Test quote")
        
        valid_profiles = ["warm", "cool", "neutral", "ethereal", "cosmic", "grounded"]
        assert analysis["color_profile"] in valid_profiles
    
    def test_fallback_has_keywords_list(self):
        """Test that fallback has a list of style keywords."""
        analysis = create_fallback_analysis("Test quote")
        
        assert isinstance(analysis["style_keywords"], list)
        assert len(analysis["style_keywords"]) > 0


class TestQuoteCard:
    """Tests for QuoteCard class."""
    
    def test_card_initialization(self):
        """Test that QuoteCard initializes correctly."""
        card = QuoteCard()
        
        assert card.card_type == "quote"
        assert card.width == 480
        assert card.height == 200
    
    def test_wrap_text_single_line(self):
        """Test text wrapping with short text."""
        card = QuoteCard()
        text = "Short quote"
        lines = card.wrap_text(text, max_chars_per_line=45)
        
        assert len(lines) == 1
        assert lines[0] == "Short quote"
    
    def test_wrap_text_multiple_lines(self):
        """Test text wrapping with long text."""
        card = QuoteCard()
        text = "This is a much longer quote that definitely needs to be wrapped across multiple lines to fit properly"
        lines = card.wrap_text(text, max_chars_per_line=40)
        
        assert len(lines) > 1
        for line in lines:
            assert len(line) <= 40
    
    def test_wrap_text_preserves_words(self):
        """Test that text wrapping doesn't break words."""
        card = QuoteCard()
        text = "The only way to do great work is to love what you do"
        lines = card.wrap_text(text, max_chars_per_line=30)
        
        # Reconstruct text and verify it matches original
        reconstructed = " ".join(lines)
        assert reconstructed == text
    
    def test_get_palette_gradient_neutral(self):
        """Test getting neutral palette gradient."""
        card = QuoteCard()
        card.analysis_data = {"color_profile": "neutral"}
        
        gradient = card.get_palette_gradient()
        
        assert isinstance(gradient, tuple)
        assert len(gradient) == 2
        # Should be hex colors
        assert gradient[0].startswith("#")
        assert gradient[1].startswith("#")
    
    def test_get_palette_gradient_warm(self):
        """Test getting warm palette gradient."""
        card = QuoteCard()
        card.analysis_data = {"color_profile": "warm"}
        
        gradient = card.get_palette_gradient()
        
        assert isinstance(gradient, tuple)
        assert len(gradient) == 2
        assert gradient[0].startswith("#")
        assert gradient[1].startswith("#")
    
    def test_get_palette_gradient_fallback(self):
        """Test gradient fallback when profile doesn't exist."""
        card = QuoteCard()
        card.analysis_data = {"color_profile": "nonexistent"}
        
        gradient = card.get_palette_gradient()
        
        # Should fall back to default background gradient
        assert isinstance(gradient, tuple)
        assert len(gradient) == 2
    
    def test_generate_card_with_quote(self):
        """Test generating a card with quote data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test quote
            quote_path = Path(tmpdir) / "quote.json"
            quote_data = {
                "quote": "Test quote for validation",
                "author": "Test Author"
            }
            with open(quote_path, 'w') as f:
                json.dump(quote_data, f)
            
            # Create test analysis
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_data = {
                "sentiment": "uplifting",
                "tone": "hopeful",
                "theme": "wisdom",
                "color_profile": "warm",
                "style_keywords": ["sunrise"]
            }
            with open(analysis_path, 'w') as f:
                json.dump(analysis_data, f)
            
            # Generate card
            card = QuoteCard()
            card.load_data(str(quote_path), str(analysis_path))
            
            assert card.quote_data["quote"] == "Test quote for validation"
            assert card.analysis_data["color_profile"] == "warm"
    
    def test_generate_card_missing_analysis(self):
        """Test generating a card when analysis is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test quote
            quote_path = Path(tmpdir) / "quote.json"
            quote_data = {
                "quote": "Test quote",
                "author": "Test Author"
            }
            with open(quote_path, 'w') as f:
                json.dump(quote_data, f)
            
            # Don't create analysis file
            analysis_path = Path(tmpdir) / "analysis.json"
            
            # Should not raise, should use fallback
            card = QuoteCard()
            card.load_data(str(quote_path), str(analysis_path))
            
            # Should have fallback analysis
            assert card.analysis_data["color_profile"] == "neutral"
    
    def test_build_stylistic_effects_sunrise(self):
        """Test building sunrise effect."""
        card = QuoteCard()
        card.analysis_data = {"style_keywords": ["sunrise"]}
        
        effects = card.build_stylistic_effects()
        
        assert "Sunrise effect" in effects
        assert "rect" in effects
    
    def test_build_stylistic_effects_cosmic(self):
        """Test building cosmic effect."""
        card = QuoteCard()
        card.analysis_data = {"style_keywords": ["cosmic"]}
        
        effects = card.build_stylistic_effects()
        
        assert "circle" in effects
    
    def test_build_stylistic_effects_storm(self):
        """Test building storm effect."""
        card = QuoteCard()
        card.analysis_data = {"style_keywords": ["storm"]}
        
        effects = card.build_stylistic_effects()
        
        assert "line" in effects
    
    def test_build_stylistic_effects_gentle(self):
        """Test building gentle/vignette effect."""
        card = QuoteCard()
        card.analysis_data = {"style_keywords": ["gentle"]}
        
        effects = card.build_stylistic_effects()
        
        assert "Vignette effect" in effects
    
    def test_build_stylistic_effects_none(self):
        """Test with no stylistic effects."""
        card = QuoteCard()
        card.analysis_data = {"style_keywords": []}
        
        effects = card.build_stylistic_effects()
        
        assert effects == ""
    
    def test_generate_content_basic(self):
        """Test generating basic content."""
        card = QuoteCard()
        card.quote_data = {
            "quote": "Test quote",
            "author": "Test Author"
        }
        card.analysis_data = {
            "sentiment": "hopeful",
            "theme": "wisdom",
            "style_keywords": []
        }
        
        content = card.generate_content()
        
        assert "Test quote" in content
        assert "Test Author" in content
        assert "text" in content  # SVG text elements
    
    def test_generate_content_no_author(self):
        """Test generating content without author."""
        card = QuoteCard()
        card.quote_data = {
            "quote": "Test quote"
        }
        card.analysis_data = {
            "sentiment": "hopeful",
            "theme": "wisdom",
            "style_keywords": []
        }
        
        content = card.generate_content()
        
        assert "Test quote" in content
        # Author section should be empty or minimal
    
    def test_generate_svg_complete(self):
        """Test generating complete SVG."""
        card = QuoteCard()
        card.quote_data = {
            "quote": "Test quote",
            "author": "Test Author"
        }
        card.analysis_data = {
            "sentiment": "hopeful",
            "theme": "wisdom",
            "color_profile": "warm",
            "style_keywords": []
        }
        
        svg = card.generate_svg()
        
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert "Test quote" in svg
        assert "linearGradient" in svg
        assert 'width="480"' in svg
        assert 'height="200"' in svg


class TestQuoteValidation:
    """Tests for quote data validation."""
    
    def test_empty_quote_handled(self):
        """Test handling of empty quote."""
        card = QuoteCard()
        card.quote_data = {"quote": "", "author": ""}
        card.analysis_data = {"style_keywords": [], "sentiment": "", "theme": ""}
        
        # Should not crash
        content = card.generate_content()
        assert "Quote not available" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
