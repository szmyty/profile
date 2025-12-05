#!/usr/bin/env python3
"""
Generate a styled SVG card for Quote of the Day with theme-matched background.

This script reads:
- quotes/quote.json (the quote text and author)
- quotes/quote_analysis.json (LLM analysis of sentiment/theme/color)

And generates a visually expressive SVG card with:
- Dynamic gradient background matching quote's emotional tone
- Optional stylistic decorations based on keywords
- Typography optimized for readability
- Full integration with theme.json and CardBase
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.card_base import CardBase
from lib.utils import (
    escape_xml,
    load_json,
    safe_get,
)


class QuoteCard(CardBase):
    """Generate a Quote of the Day card with theme-matched background."""
    
    def __init__(self):
        """Initialize the Quote card generator."""
        super().__init__("quote")
        self.quote_data: Dict[str, Any] = {}
        self.analysis_data: Dict[str, Any] = {}
    
    def load_data(self, quote_path: str, analysis_path: str) -> None:
        """
        Load quote and analysis data.
        
        Args:
            quote_path: Path to quote.json
            analysis_path: Path to quote_analysis.json
        """
        self.quote_data = load_json(quote_path, "quote")
        
        # Analysis is optional - if not available, use neutral palette
        try:
            with open(analysis_path, 'r') as f:
                self.analysis_data = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: Analysis file not found: {analysis_path}, using neutral palette")
            self.analysis_data = {
                "color_profile": "neutral",
                "style_keywords": [],
                "sentiment": "reflective",
                "tone": "contemplative"
            }
        except (json.JSONDecodeError, IOError, PermissionError) as e:
            print(f"⚠️  Warning: Could not load analysis from {analysis_path}: {e}, using neutral palette")
            self.analysis_data = {
                "color_profile": "neutral",
                "style_keywords": [],
                "sentiment": "reflective",
                "tone": "contemplative"
            }
    
    def get_palette_gradient(self) -> Tuple[str, str]:
        """
        Get the gradient colors based on quote analysis.
        
        Returns:
            Tuple of (start_color, end_color) for gradient
        """
        color_profile = self.analysis_data.get("color_profile", "neutral")
        
        # Try to get emotion palette from theme
        gradient = self.get_gradient(f"emotion.{color_profile}")
        
        # If gradient is found, return it
        if gradient and len(gradient) == 2:
            return (gradient[0], gradient[1])
        
        # Fallback to default background gradient
        default_gradient = self.get_gradient("background.default")
        return (default_gradient[0], default_gradient[1])
    
    def wrap_text(self, text: str, max_chars_per_line: int = 45) -> List[str]:
        """
        Wrap text to fit within card width, breaking at word boundaries.
        
        Args:
            text: Text to wrap
            max_chars_per_line: Maximum characters per line
            
        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def build_stylistic_effects(self) -> str:
        """
        Build optional stylistic effects based on keywords.
        
        Effects include:
        - "sunrise"/"sky": horizontal gradient band
        - "storm"/"rain": subtle diagonal streaks
        - "cosmic"/"universe": light starfield
        - "gentle"/"soft": low-opacity vignette
        
        Returns:
            SVG string with effects
        """
        keywords = self.analysis_data.get("style_keywords", [])
        if not keywords:
            return ""
        
        effects = []
        
        # Sunrise/sky: horizontal gradient band at top
        if any(kw in keywords for kw in ["sunrise", "sunset", "sky"]):
            accent_color = self.get_color("text", "accent")
            effects.append(f'''
    <!-- Sunrise effect -->
    <rect x="0" y="20" width="{self.width}" height="2" fill="{accent_color}" opacity="0.3"/>
    <rect x="0" y="25" width="{self.width}" height="1" fill="{accent_color}" opacity="0.2"/>''')
        
        # Storm/rain: diagonal streaks
        if any(kw in keywords for kw in ["storm", "rain"]):
            text_muted = self.get_color("text", "muted")
            for i, x in enumerate([100, 250, 400]):
                y = 30 + (i * 40)
                effects.append(f'''
    <line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y + 60}" stroke="{text_muted}" stroke-width="1" opacity="0.15"/>''')
        
        # Cosmic/universe: subtle starfield
        if any(kw in keywords for kw in ["cosmic", "universe", "starfield"]):
            accent_color = self.get_color("text", "accent")
            # Calculate star positions dynamically based on card dimensions
            star_positions = [
                (self.width * 0.1, self.height * 0.2),
                (self.width * 0.3, self.height * 0.35),
                (self.width * 0.7, self.height * 0.25),
                (self.width * 0.85, self.height * 0.5),
                (self.width * 0.55, self.height * 0.7),
            ]
            for x, y in star_positions:
                effects.append(f'''
    <circle cx="{x}" cy="{y}" r="1.5" fill="{accent_color}" opacity="0.4"/>''')
        
        # Gentle/soft: vignette effect
        if any(kw in keywords for kw in ["gentle", "soft", "calm"]):
            effects.append(f'''
    <!-- Vignette effect -->
    <rect x="0" y="0" width="{self.width}" height="{self.height}" fill="black" opacity="0.05" rx="{self.get_border_radius('xl')}"/>''')
        
        return '\n'.join(effects)
    
    def generate_content(self) -> str:
        """
        Generate the quote card content.
        
        Returns:
            SVG content string
        """
        quote = self.quote_data.get("quote", "")
        author = self.quote_data.get("author", "")
        
        if not quote:
            quote = "Quote not available"
        
        # Escape text for XML
        escaped_quote = escape_xml(quote)
        escaped_author = escape_xml(author)
        
        # Wrap quote text
        quote_lines = self.wrap_text(quote, max_chars_per_line=45)
        
        # Typography
        font_family = self.get_typography("font_family")
        quote_font_size = self.get_font_size("xl")
        author_font_size = self.get_font_size("md")
        
        # Colors
        text_primary = self.get_color("text", "primary")
        text_secondary = self.get_color("text", "secondary")
        accent_color = self.get_color("text", "accent")
        
        # Build quote text lines
        quote_y_start = 50
        line_height = quote_font_size + 6
        quote_svg_lines = []
        
        for i, line in enumerate(quote_lines):
            y = quote_y_start + (i * line_height)
            quote_svg_lines.append(
                f'    <text x="30" y="{y}" font-family="{font_family}" font-size="{quote_font_size}" '
                f'fill="{text_primary}" font-style="italic">{escape_xml(line)}</text>'
            )
        
        quote_text_svg = '\n'.join(quote_svg_lines)
        
        # Author position (below quote)
        author_y = quote_y_start + (len(quote_lines) * line_height) + 20
        
        # Author attribution
        author_svg = ""
        if author:
            author_svg = f'''
    <text x="30" y="{author_y}" font-family="{font_family}" font-size="{author_font_size}" fill="{text_secondary}">— {escaped_author}</text>'''
        
        # Quote marks decoration
        quote_mark_size = self.get_font_size("6xl")
        quote_marks = f'''
    <!-- Opening quote mark -->
    <text x="15" y="35" font-family="{font_family}" font-size="{quote_mark_size}" fill="{accent_color}" opacity="0.3">"</text>'''
        
        # Stylistic effects based on keywords
        effects = self.build_stylistic_effects()
        
        # Sentiment/theme badge (subtle)
        sentiment = self.analysis_data.get("sentiment", "")
        theme = self.analysis_data.get("theme", "")
        
        badge_svg = ""
        if sentiment or theme:
            badge_text = f"{sentiment.title()}"
            if theme:
                badge_text += f" • {theme.title()}"
            
            badge_y = self.height - 15
            badge_svg = f'''
    <!-- Sentiment badge -->
    <text x="30" y="{badge_y}" font-family="{font_family}" font-size="{self.get_font_size('xs')}" fill="{text_secondary}" opacity="0.7">{escape_xml(badge_text)}</text>'''
        
        return f'''
  <!-- Stylistic effects -->
  {effects}
  
  <!-- Quote marks -->
  {quote_marks}
  
  <!-- Quote text -->
  <g id="quote-content">
{quote_text_svg}
{author_svg}
  </g>
  
  <!-- Sentiment/theme badge -->
  {badge_svg}
'''


def main():
    """Main entry point for quote card generation."""
    # Default paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    quote_path = repo_root / "quotes" / "quote.json"
    analysis_path = repo_root / "quotes" / "quote_analysis.json"
    output_path = repo_root / "quotes" / "quote_card.svg"
    
    # Allow overriding via command line
    if len(sys.argv) > 1:
        quote_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        analysis_path = Path(sys.argv[2])
    if len(sys.argv) > 3:
        output_path = Path(sys.argv[3])
    
    try:
        # Create card generator
        card = QuoteCard()
        
        # Load data
        print(f"📖 Loading quote from {quote_path}")
        print(f"🎨 Loading analysis from {analysis_path}")
        card.load_data(str(quote_path), str(analysis_path))
        
        # Get palette gradient
        gradient = card.get_palette_gradient()
        print(f"🎨 Using gradient: {gradient[0]} → {gradient[1]}")
        
        # Generate SVG
        print("🎨 Generating quote card...")
        svg_content = card.generate_svg(
            bg_gradient=gradient,
            include_glow=True,
            include_shadow=False,
            include_decorative_accent=True,
        )
        
        # Write output
        card.write_svg(str(output_path), svg_content)
        print(f"✅ Quote card generated: {output_path}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating quote card: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
