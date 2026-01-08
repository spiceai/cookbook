#!/bin/bash

# AI SQL Function Example Queries Script
# This script demonstrates various uses of the ai() SQL function

echo "🚀 AI SQL Function Examples"
echo "=================="
echo ""
echo "Make sure Spice is running with: spice run"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a query and display results
run_query() {
    local title="$1"
    local query="$2"
    
    echo -e "${BLUE}Example: ${title}${NC}"
    echo "Query:"
    echo "$query"
    echo ""
    echo "Result:"
    spice sql --query "$query"
    echo ""
    echo "---"
    echo ""
}

# Example 1: Simple greeting
run_query "Simple AI Greeting" \
"SELECT ai('Say hello in a creative way!', 'gpt-4o-mini') as greeting;"

# Example 2: Categorize zones
run_query "Categorize NYC Zones" \
"SELECT LocationID, Zone, ai(concat('Categorize this location in one word: ', Zone), 'gpt-4o-mini') as category FROM taxi_zones LIMIT 5;"

# Example 3: Sentiment analysis
run_query "Sentiment Analysis" \
"SELECT id, feedback, ai('Classify this feedback as positive, negative, or neutral: ' || feedback, 'gpt-4o-mini') as sentiment FROM customer_feedback LIMIT 3;"

# Example 4: Question answering
run_query "AI Question Answering" \
"SELECT ai('What is the capital of France? Answer in one word.', 'gpt-4o-mini') as answer;"

# Example 5: Data enrichment
run_query "Generate Descriptions" \
"SELECT Zone, Borough, left(ai('Write a brief one-sentence description of ' || Zone || ' in ' || Borough, 'gpt-4o-mini'), 80) as description FROM taxi_zones WHERE Borough = 'Manhattan' LIMIT 3;"

# Example 6: Translation
run_query "Translate to Multiple Languages" \
"SELECT Zone as original, ai(concat_ws(' ', 'Translate to Spanish:', Zone), 'gpt-4o-mini') as spanish, ai(concat_ws(' ', 'Translate to French:', Zone), 'gpt-4o-mini') as french FROM taxi_zones WHERE Borough = 'Manhattan' LIMIT 3;"

echo -e "${GREEN}✅ All examples completed!${NC}"
echo ""
echo "💡 Try your own queries with: spice sql"
echo ""
