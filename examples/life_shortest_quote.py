"""
Find Shortest Quote with Theme "life"

This script reads quotes from real_train.csv, filters for quotes with "life" theme,
and finds the shortest one using X-Ray SDK for tracking.
"""

import csv
import os
import sys
from typing import List, Dict, Any

# Add parent directory to path to import sdk
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sdk import XRay, step


def load_quotes_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load and parse quotes from CSV file."""
    quotes = []
    
    required_columns = ['theme', 'quote_id', 'text', 'length']
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Strip BOM and whitespace from fieldnames
        if reader.fieldnames:
            reader.fieldnames = [name.strip().lstrip('\ufeff') for name in reader.fieldnames]
        
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"CSV file is missing required columns: {missing_columns}. "
                           f"Found columns: {list(reader.fieldnames)}")
        
        for row in reader:
            try:
                quote = {
                    'quote_id': row['quote_id'],
                    'theme': row['theme'],
                    'text': row['text'],
                    'length': int(row['length'])
                }
                quotes.append(quote)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return quotes


def find_shortest_life_quote():
    """Main function to find shortest quote with 'life' theme using X-Ray SDK."""
    
    # Initialize X-Ray
    xray = XRay("find_shortest_life_quote", api_url="http://localhost:8000")
    
    # Start execution
    xray.start_execution(metadata={
        "environment": "production",
        "task": "find_shortest_quote",
        "theme": "life",
        "criteria": "shortest_length"
    })
    
    # Step 1: Load Quotes from CSV
    with step(xray, "Load Quotes from CSV", step_type="load",
              input_data={"csv_file": "real_train.csv"}) as step_ctx:
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "real_train.csv")
        quotes = load_quotes_from_csv(csv_path)
        
        # Record each quote as loaded
        for quote in quotes:
            step_ctx.log_evaluation(
                entity_id=quote['quote_id'],
                value={
                    "theme": quote['theme'],
                    "length": quote['length'],
                    "text_preview": quote['text'][:50] + "..." if len(quote['text']) > 50 else quote['text']
                },
                passed=True,
                reason=f"Loaded quote {quote['quote_id']} from CSV"
            )
        
        step_ctx.set_output({
            "total_quotes_loaded": len(quotes),
            "sample_quote_ids": [q["quote_id"] for q in quotes[:5]]
        })
    
    print(f"✅ Loaded {len(quotes)} quotes from CSV")
    
    # Step 2: Filter by Theme "life"
    with step(xray, "Filter by Theme 'life'", step_type="filter",
              input_data={"theme": "life"},
              rules=[{
                  "rule_id": "theme_contains_life",
                  "description": "Quote theme must contain 'life'",
                  "operator": "contains",
                  "value": "life",
                  "source": "config"
              }]) as step_ctx:
        
        life_quotes = []
        for quote in quotes:
            # Check if theme contains "life" (case-insensitive)
            theme_lower = quote['theme'].lower()
            has_life_theme = 'life' in theme_lower
            
            step_ctx.evaluate(
                entity_id=quote['quote_id'],
                value=quote['theme'],
                condition=has_life_theme,
                reason=f"Theme check: {'contains' if has_life_theme else 'does not contain'} 'life'"
            )
            
            if has_life_theme:
                life_quotes.append(quote)
        
        step_ctx.set_output({
            "filtered_count": len(life_quotes),
            "passed": len(life_quotes),
            "failed": len(quotes) - len(life_quotes),
            "life_quote_ids": [q["quote_id"] for q in life_quotes]
        })
    
    print(f"✅ Filtered to {len(life_quotes)} quotes with 'life' theme")
    
    if not life_quotes:
        print("❌ No quotes found with 'life' theme!")
        xray.end_execution(status="completed")
        return None
    
    # Step 3: Find Shortest Quote
    with step(xray, "Find Shortest Quote", step_type="select",
              input_data={"selection_criteria": "minimum length"}) as step_ctx:
        
        # Find quote with minimum length
        shortest_quote = min(life_quotes, key=lambda x: x['length'])
        
        # Record all life quotes with their lengths for comparison
        for quote in life_quotes:
            is_shortest = quote['quote_id'] == shortest_quote['quote_id']
            step_ctx.log_evaluation(
                entity_id=quote['quote_id'],
                value={
                    "length": quote['length'],
                    "text_preview": quote['text'][:50] + "..." if len(quote['text']) > 50 else quote['text']
                },
                passed=is_shortest,
                reason=f"Length: {quote['length']} characters - {'SHORTEST' if is_shortest else 'longer than shortest'}"
            )
        
        step_ctx.set_output({
            "selected_quote_id": shortest_quote['quote_id'],
            "selected_length": shortest_quote['length'],
            "selected_text": shortest_quote['text'],
            "selected_theme": shortest_quote['theme'],
            "total_candidates": len(life_quotes),
            "length_comparison": {
                "shortest": shortest_quote['length'],
                "longest": max(q['length'] for q in life_quotes),
                "average": sum(q['length'] for q in life_quotes) / len(life_quotes)
            }
        })
    
    print(f"✅ Found shortest quote: ID {shortest_quote['quote_id']} ({shortest_quote['length']} chars)")
    
    # End execution
    xray.end_execution(status="completed")
    
    # Print results
    print("\n" + "="*70)
    print("🎯 SHORTEST QUOTE WITH 'LIFE' THEME")
    print("="*70)
    print(f"Quote ID: {shortest_quote['quote_id']}")
    print(f"Theme: {shortest_quote['theme']}")
    print(f"Length: {shortest_quote['length']} characters")
    print(f"\nQuote Text:")
    print(f"  \"{shortest_quote['text']}\"")
    print("="*70)
    print(f"\n✅ Execution completed! Check dashboard at http://localhost:3000")
    print(f"   Execution ID: {xray.execution_id}")
    
    return shortest_quote


if __name__ == "__main__":
    print("="*70)
    print("Find Shortest Quote with Theme 'life'")
    print("="*70)
    print()
    
    try:
        shortest = find_shortest_life_quote()
        if shortest:
            print("\n✅ Successfully found shortest quote with 'life' theme!")
        else:
            print("\n❌ No quotes found with 'life' theme.")
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

