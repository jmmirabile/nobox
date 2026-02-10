#!/bin/bash
# NoBox Demo Script - Showcasing hierarchical discovery features
# This script demonstrates the complete workflow of NoBox

set -e  # Exit on error

echo "========================================"
echo "NoBox Demo - Hierarchical Discovery"
echo "========================================"
echo ""

# Clean up any existing demo data
echo "🧹 Cleaning up old demo data..."
rm -rf ~/.local/share/nobox/json/demo 2>/dev/null || true
echo ""

# Level 1: List databases (should be empty for demo)
echo "📂 Level 1: List all databases"
echo "$ jb -l"
jb -l || echo "No databases yet"
echo ""

# Create some demo data
echo "✏️  Creating demo data..."
echo "$ jb demo contacts set alice name:Alice email:alice@example.com phone:555-1234"
jb demo contacts set alice name:Alice email:alice@example.com phone:555-1234

echo "$ jb demo contacts set bob name:Bob email:bob@example.com department:engineering"
jb demo contacts set bob name:Bob email:bob@example.com department:engineering

echo "$ jb demo projects set website name:Website status:active priority:high"
jb demo projects set website name:Website status:active priority:high

echo "$ jb demo projects set mobile name:"Mobile App" status:planning priority:medium"
jb demo projects set mobile name:"Mobile App" status:planning priority:medium
echo ""

# Level 1: List databases again
echo "📂 Level 1: List all databases (after creating data)"
echo "$ jb -l"
jb -l
echo ""

# Level 2: List collections
echo "📁 Level 2: List collections in 'demo' database"
echo "$ jb demo -l"
jb demo -l
echo ""

# Alternative syntax
echo "📁 Using explicit command: jb demo collections"
echo "$ jb demo collections"
jb demo collections
echo ""

# Level 3: List keys
echo "🔑 Level 3: List keys in 'contacts' collection"
echo "$ jb demo contacts keys"
jb demo contacts keys
echo ""

# Level 4: View records
echo "📄 Level 4: View all contacts"
echo "$ jb demo contacts all"
jb demo contacts all
echo ""

# Show different output formats
echo "🎨 Different output formats:"
echo ""

echo "JSON format:"
echo "$ jb demo contacts all --json"
jb demo contacts all --json
echo ""

echo "JSON Lines format:"
echo "$ jb demo contacts all --jsonl"
jb demo contacts all --jsonl
echo ""

echo "One-line format (great for grep/awk):"
echo "$ jb demo contacts all --oneline"
jb demo contacts all --oneline
echo ""

echo "CSV format (for Excel):"
echo "$ jb demo contacts all --csv"
jb demo contacts all --csv
echo ""

# Query examples
echo "🔍 Query examples:"
echo ""

echo "Get a specific record:"
echo "$ jb demo contacts get alice"
jb demo contacts get alice
echo ""

echo "Using grep with one-line format:"
echo "$ jb demo contacts all --oneline | grep engineering"
jb demo contacts all --oneline | grep engineering
echo ""

echo "Using jq for complex queries:"
echo '$ jb demo contacts all --json | jq ".[] | select(.department)"'
jb demo contacts all --json | jq '.[] | select(.department)'
echo ""

# Show YAML format works too
echo "📝 YAML format works the same way:"
echo "$ yb demo notes set todo1 task:\"Update documentation\" priority:high"
yb demo notes set todo1 task:"Update documentation" priority:high

echo "$ yb demo -l"
yb demo -l
echo ""

echo "$ yb demo notes all"
yb demo notes all
echo ""

# Summary
echo "========================================"
echo "✅ Demo Complete!"
echo "========================================"
echo ""
echo "Key takeaways:"
echo "  • jb -l          → List databases"
echo "  • jb demo -l     → List collections"
echo "  • jb demo contacts keys → List keys"
echo "  • Multiple output formats (table, JSON, CSV, etc.)"
echo "  • Works the same for YAML (yb)"
echo ""
echo "Try it yourself! Your demo data is in: ~/.local/share/nobox/json/demo/"
echo ""
