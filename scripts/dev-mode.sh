#!/bin/bash
# Development mode script - Generate cards using mock data
# Usage: ./scripts/dev-mode.sh [card-type]
# Card types: soundcloud, weather, developer, oura, all

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MOCK_DATA_DIR="$REPO_ROOT/data/mock"
OUTPUT_DIR="$REPO_ROOT/dev-output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Running in Development Mode${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

generate_soundcloud() {
    echo -e "${GREEN}🎵 Generating SoundCloud card...${NC}"
    python "$SCRIPT_DIR/generate-card.py" \
        "$MOCK_DATA_DIR/soundcloud-metadata.json" \
        "$MOCK_DATA_DIR/soundcloud-artwork.jpg" \
        "$OUTPUT_DIR/soundcloud-card.svg" 2>/dev/null || {
        # If artwork doesn't exist, create a placeholder
        python -c "from PIL import Image; img = Image.new('RGB', (400, 400), color='#1e1e1e'); img.save('$MOCK_DATA_DIR/soundcloud-artwork.jpg')"
        python "$SCRIPT_DIR/generate-card.py" \
            "$MOCK_DATA_DIR/soundcloud-metadata.json" \
            "$MOCK_DATA_DIR/soundcloud-artwork.jpg" \
            "$OUTPUT_DIR/soundcloud-card.svg"
    }
    echo -e "   → Saved to: ${YELLOW}$OUTPUT_DIR/soundcloud-card.svg${NC}"
}

generate_weather() {
    echo -e "${GREEN}🌦️  Generating Weather card...${NC}"
    python "$SCRIPT_DIR/generate-weather-card.py" \
        "$MOCK_DATA_DIR/weather.json" \
        "$OUTPUT_DIR/weather-today.svg"
    echo -e "   → Saved to: ${YELLOW}$OUTPUT_DIR/weather-today.svg${NC}"
}

generate_developer() {
    echo -e "${GREEN}💻 Generating Developer dashboard...${NC}"
    python "$SCRIPT_DIR/generate-developer-dashboard.py" \
        "$MOCK_DATA_DIR/developer-stats.json" \
        "$OUTPUT_DIR/developer-dashboard.svg"
    echo -e "   → Saved to: ${YELLOW}$OUTPUT_DIR/developer-dashboard.svg${NC}"
}

generate_oura() {
    echo -e "${GREEN}🧬 Generating Oura health dashboard...${NC}"
    
    # Generate health snapshot
    python "$SCRIPT_DIR/generate-health-snapshot.py" \
        "$MOCK_DATA_DIR/oura-metrics.json" \
        "$OUTPUT_DIR/health-snapshot.json"
    
    # Generate health dashboard
    python "$SCRIPT_DIR/generate-health-dashboard.py" \
        "$OUTPUT_DIR/health-snapshot.json" \
        "$OUTPUT_DIR/health-dashboard.svg"
    
    # Generate mood data
    python "$SCRIPT_DIR/oura-mood-engine.py" \
        "$MOCK_DATA_DIR/oura-metrics.json" \
        "$OUTPUT_DIR/mood.json"
    
    # Generate mood dashboard
    python "$SCRIPT_DIR/generate-oura-mood-card.py" \
        "$OUTPUT_DIR/mood.json" \
        "$MOCK_DATA_DIR/oura-metrics.json" \
        "$OUTPUT_DIR/mood-dashboard.svg"
    
    echo -e "   → Saved to: ${YELLOW}$OUTPUT_DIR/health-dashboard.svg${NC}"
    echo -e "   → Saved to: ${YELLOW}$OUTPUT_DIR/mood-dashboard.svg${NC}"
}

# Parse command line arguments
CARD_TYPE="${1:-all}"

case "$CARD_TYPE" in
    soundcloud)
        generate_soundcloud
        ;;
    weather)
        generate_weather
        ;;
    developer)
        generate_developer
        ;;
    oura)
        generate_oura
        ;;
    all)
        generate_soundcloud
        echo ""
        generate_weather
        echo ""
        generate_developer
        echo ""
        generate_oura
        ;;
    *)
        echo "Unknown card type: $CARD_TYPE"
        echo "Usage: $0 [soundcloud|weather|developer|oura|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Development mode complete!${NC}"
echo -e "${BLUE}All outputs saved to: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""
