#!/usr/bin/env python3
"""
Analyze a quote using LLM to determine sentiment, emotional tone, and aesthetic properties.

This script reads a quote from quotes/quote.json and uses OpenAI's API to analyze:
- Sentiment (positive, negative, neutral, uplifting, melancholic, etc.)
- Emotional tone (hopeful, reflective, inspiring, calm, etc.)
- Thematic category (renewal, wisdom, courage, nature, etc.)
- Aesthetic keywords (sunrise, storm, cosmic, gentle, etc.)
- Color profile/palette hints (warm, cool, neutral, ethereal, cosmic, grounded)

Output is written to quotes/quote_analysis.json for use by the card generator.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def load_quote(quote_path: str) -> Dict[str, Any]:
    """
    Load quote data from JSON file.
    
    Args:
        quote_path: Path to quote.json file
        
    Returns:
        Quote data dictionary
        
    Raises:
        FileNotFoundError: If quote file doesn't exist
        json.JSONDecodeError: If quote file is invalid JSON
    """
    with open(quote_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_quote_with_llm(quote: str, author: str = "", model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Use OpenAI to analyze quote and extract emotional/aesthetic properties.
    
    Args:
        quote: The quote text to analyze
        author: Optional author name
        model: OpenAI model to use (default: gpt-4o-mini)
        
    Returns:
        Analysis dictionary with sentiment, tone, theme, color_profile, and keywords
        
    Raises:
        RuntimeError: If OpenAI is not available or API call fails
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError("OpenAI library not installed. Install with: pip install openai")
    
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    client = OpenAI(api_key=api_key)
    
    # Construct the analysis prompt
    author_text = f" by {author}" if author else ""
    prompt = f"""Analyze the following quote{author_text} and provide a JSON response with these exact fields:

Quote: "{quote}"

Provide analysis in this exact JSON format:
{{
  "sentiment": "<one word: uplifting, hopeful, melancholic, inspiring, reflective, peaceful, energetic, somber, etc.>",
  "tone": "<one word: gentle, bold, introspective, encouraging, contemplative, serene, passionate, etc.>",
  "theme": "<one word: renewal, wisdom, courage, nature, time, journey, love, growth, etc.>",
  "color_profile": "<exactly one: warm, cool, neutral, ethereal, cosmic, grounded>",
  "style_keywords": [<1-3 keywords from: sunrise, sunset, sky, storm, rain, cosmic, universe, gentle, soft, bold, bright, dark, misty, clear, starfield, etc.>]
}}

Choose color_profile based on the quote's emotional temperature and aesthetic:
- warm: optimistic, energetic, passionate, sunrise themes
- cool: calm, peaceful, introspective, sky/water themes
- neutral: balanced, timeless, grounded wisdom
- ethereal: dreamy, transcendent, mystical, soft
- cosmic: vast, universal, existential, space themes
- grounded: earthy, practical, stable, nature-rooted

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing quotes for emotional tone and aesthetic qualities. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent responses
            max_tokens=200
        )
        
        # Extract and parse JSON response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        analysis = json.loads(content)
        
        # Validate required fields
        required_fields = ["sentiment", "tone", "theme", "color_profile", "style_keywords"]
        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate color_profile is one of the allowed values
        valid_profiles = ["warm", "cool", "neutral", "ethereal", "cosmic", "grounded"]
        if analysis["color_profile"] not in valid_profiles:
            # Default to neutral if invalid
            print(f"Warning: Invalid color_profile '{analysis['color_profile']}', defaulting to 'neutral'", file=sys.stderr)
            analysis["color_profile"] = "neutral"
        
        return analysis
        
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
    except Exception as e:
        raise RuntimeError(f"Failed to analyze quote with LLM: {e}")


def create_fallback_analysis(quote: str, author: str = "") -> Dict[str, Any]:
    """
    Create a fallback analysis when LLM is not available.
    
    Args:
        quote: The quote text
        author: Optional author name
        
    Returns:
        Basic neutral analysis dictionary
    """
    return {
        "sentiment": "reflective",
        "tone": "contemplative",
        "theme": "wisdom",
        "color_profile": "neutral",
        "style_keywords": ["gentle", "soft"],
        "fallback": True,
        "fallback_reason": "LLM not available or API key not set"
    }


def save_analysis(analysis: Dict[str, Any], output_path: str, llm_version: str = "gpt-4o-mini") -> None:
    """
    Save quote analysis to JSON file with metadata.
    
    Args:
        analysis: Analysis dictionary from LLM
        output_path: Path to write quote_analysis.json
        llm_version: Model version used for analysis
    """
    # Add metadata
    output_data = {
        **analysis,
        "llm_version": llm_version,
        "interpreted_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Quote analysis saved to {output_path}")


def main():
    """Main entry point for quote analysis."""
    # Default paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    quote_path = repo_root / "quotes" / "quote.json"
    output_path = repo_root / "quotes" / "quote_analysis.json"
    
    # Allow overriding paths via command line arguments
    if len(sys.argv) > 1:
        quote_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    
    try:
        # Load quote
        print(f"📖 Loading quote from {quote_path}")
        quote_data = load_quote(str(quote_path))
        
        quote_text = quote_data.get("quote", "")
        author = quote_data.get("author", "")
        
        if not quote_text:
            print("❌ Error: No quote text found in quote.json", file=sys.stderr)
            sys.exit(1)
        
        print(f"Quote: \"{quote_text}\"")
        if author:
            print(f"Author: {author}")
        
        # Try to analyze with LLM
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        
        try:
            print(f"🤖 Analyzing quote with {model}...")
            analysis = analyze_quote_with_llm(quote_text, author, model)
            print(f"✅ Analysis complete:")
            print(f"  Sentiment: {analysis['sentiment']}")
            print(f"  Tone: {analysis['tone']}")
            print(f"  Theme: {analysis['theme']}")
            print(f"  Color Profile: {analysis['color_profile']}")
            print(f"  Keywords: {', '.join(analysis['style_keywords'])}")
            
        except (RuntimeError, Exception) as e:
            print(f"⚠️  Warning: LLM analysis failed: {e}", file=sys.stderr)
            print("⚠️  Using fallback neutral analysis", file=sys.stderr)
            analysis = create_fallback_analysis(quote_text, author)
        
        # Save analysis
        save_analysis(analysis, str(output_path), model)
        
        print("✅ Quote analysis complete!")
        
    except FileNotFoundError:
        print(f"❌ Error: Quote file not found: {quote_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in quote file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
