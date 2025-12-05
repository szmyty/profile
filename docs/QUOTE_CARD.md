# Quote of the Day Card Generator

This feature generates a dynamic, theme-matched Quote of the Day card that adapts its visual style based on the emotional tone and meaning of the quote.

## Overview

The quote card system consists of two main components:

1. **Quote Analysis** (`scripts/analyze_quote.py`): Uses LLM to analyze quotes and extract emotional/aesthetic properties
2. **Card Generation** (`scripts/generate_quote_card.py`): Creates SVG cards with theme-matched backgrounds and stylistic effects

## Features

### Emotion-Based Color Palettes

The system includes 6 emotion-based color palettes that match the quote's emotional tone:

- **Warm**: Optimistic, energetic, passionate, sunrise themes (`#FFAD7A` → `#FF6F5E`)
- **Cool**: Calm, peaceful, introspective, sky/water themes (`#7ABEFF` → `#4A6FFF`)
- **Neutral**: Balanced, timeless, grounded wisdom (`#DCE1E7` → `#AAB1B8`)
- **Ethereal**: Dreamy, transcendent, mystical, soft (`#C8A9FF` → `#E7D1FF`)
- **Cosmic**: Vast, universal, existential, space themes (`#6A00FF` → `#B691FF`)
- **Grounded**: Earthy, practical, stable, nature-rooted (`#A26F4E` → `#D2B48C`)

### Stylistic Effects

Based on analyzed keywords, the card can include optional visual effects:

1. **Sunrise/Sky Effect**: Horizontal gradient bands for quotes about dawn, sky, or new beginnings
2. **Storm Effect**: Diagonal streaks for quotes about struggle, rain, or storms
3. **Cosmic Starfield**: Subtle stars for quotes about the universe, space, or vastness
4. **Vignette**: Soft border fade for gentle, calm, or peaceful quotes

### Intelligent Fallback

The system gracefully handles cases where the OpenAI API is unavailable:
- Falls back to a neutral palette
- Uses generic reflective/contemplative sentiment
- Still generates a functional, attractive card

## Usage

### 1. Create a Quote File

Create `quotes/quote.json` with your quote:

```json
{
  "quote": "The only way to do great work is to love what you do.",
  "author": "Steve Jobs",
  "source": "Stanford Commencement Address",
  "date": "2005-06-12"
}
```

### 2. Analyze the Quote

Run the analysis script (requires `OPENAI_API_KEY` environment variable):

```bash
export OPENAI_API_KEY="your-api-key-here"
python scripts/analyze_quote.py
```

This creates `quotes/quote_analysis.json`:

```json
{
  "sentiment": "uplifting",
  "tone": "hopeful",
  "theme": "passion",
  "color_profile": "warm",
  "style_keywords": ["sunrise", "bright"],
  "llm_version": "gpt-4o-mini",
  "interpreted_at": "2025-12-05T12:00:00Z"
}
```

### 3. Generate the Card

```bash
python scripts/generate_quote_card.py
```

This creates `quotes/quote_card.svg` with the theme-matched design.

## Configuration

### OpenAI Model

You can specify a different OpenAI model via environment variable:

```bash
export OPENAI_MODEL="gpt-4"
python scripts/analyze_quote.py
```

### Card Dimensions

Card dimensions are defined in `config/theme.json`:

```json
{
  "cards": {
    "widths": {
      "quote": 480
    },
    "heights": {
      "quote": 200
    }
  }
}
```

### Custom Palettes

You can customize emotion palettes in `config/theme.json`:

```json
{
  "gradients": {
    "emotion": {
      "warm": ["#FFAD7A", "#FF6F5E"],
      "cool": ["#7ABEFF", "#4A6FFF"],
      ...
    }
  }
}
```

## Integration with Workflow

The quote card is automatically generated as part of the build pipeline in `.github/workflows/build-profile.yml`:

1. Checks if `quotes/quote.json` exists (creates sample if not)
2. Analyzes the quote with LLM (falls back to neutral if API unavailable)
3. Generates the SVG card
4. Optimizes the SVG with SVGO
5. Updates README with the card
6. Commits changes

## Examples

### Uplifting Quote (Warm Palette)
```json
{
  "quote": "Every morning brings new potential, but only if you make the most of it.",
  "sentiment": "uplifting",
  "color_profile": "warm",
  "style_keywords": ["sunrise", "bright"]
}
```

Result: Orange-red gradient with horizontal sunrise effect

### Cosmic Quote (Cosmic Palette)
```json
{
  "quote": "Look up at the stars and not down at your feet.",
  "author": "Stephen Hawking",
  "sentiment": "inspiring",
  "color_profile": "cosmic",
  "style_keywords": ["cosmic", "starfield"]
}
```

Result: Purple gradient with subtle starfield effect

### Calm Quote (Cool Palette)
```json
{
  "quote": "In the midst of movement and chaos, keep stillness inside of you.",
  "author": "Deepak Chopra",
  "sentiment": "peaceful",
  "color_profile": "cool",
  "style_keywords": ["gentle", "calm"]
}
```

Result: Blue gradient with soft vignette

## Technical Details

### Architecture

- **CardBase Integration**: Uses the existing `CardBase` class for consistent SVG generation
- **Theme System**: Fully integrated with `theme.json` for colors, gradients, and typography
- **Modular Design**: Separate analysis and generation scripts for flexibility
- **Graceful Degradation**: Works without OpenAI API by using fallback analysis

### Text Wrapping

The card generator includes smart text wrapping:
- Wraps at word boundaries (never breaks words)
- Configurable max characters per line (default: 45)
- Automatically adjusts for quote length

### Performance

- Analysis: ~1-2 seconds with OpenAI API (cached results recommended)
- Card Generation: <100ms
- Total workflow addition: <5 seconds (with caching)

## Testing

Run the test suite:

```bash
python -m pytest tests/test_quote_card.py -v
```

The test suite includes:
- Fallback analysis validation
- Text wrapping edge cases
- Palette selection logic
- Stylistic effects generation
- SVG structure validation

## Troubleshooting

### OpenAI API Errors

If you see "OPENAI_API_KEY environment variable not set":
1. Set the environment variable: `export OPENAI_API_KEY="your-key"`
2. Or let the system use the fallback neutral analysis

### Card Not Generating

If the card fails to generate:
1. Check that `quotes/quote.json` exists and is valid JSON
2. Verify theme.json is valid
3. Check the error messages in the output
4. The workflow will create a fallback card if generation fails

### Incorrect Palette

If the palette doesn't match the quote:
1. Check `quotes/quote_analysis.json` for the analyzed values
2. Re-run analysis with a different model if needed
3. Manually edit the analysis file to override palette selection

## Future Enhancements

Potential improvements:
- Support for multi-language quotes
- Additional stylistic effects (gradients, patterns)
- Quote rotation (cycle through multiple quotes)
- Time-based quote selection
- User-defined custom effects
- Animation support (animated SVG)
