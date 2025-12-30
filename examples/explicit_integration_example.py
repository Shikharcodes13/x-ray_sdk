"""
Explicit Integration Helpers Example

This example demonstrates the explicit integration helper functions:
- filter_step() - For filtering operations
- rank_step() - For ranking operations
- transform_step() - For transformation operations
- select_step() - For selection operations

These helpers make common patterns easier while maintaining the general-purpose nature.
"""

import os
import sys

# Add parent directory to path to import sdk
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sdk import XRay, filter_step, rank_step, select_step


def explicit_integration_example():
    """Example using explicit integration helper functions."""
    
    print("=" * 70)
    print("Explicit Integration Helpers Example")
    print("=" * 70)
    print()
    
    # Initialize X-Ray
    xray = XRay("explicit_integration_demo", api_url="http://localhost:8000")
    xray.start_execution(metadata={
        "environment": "demo",
        "task": "explicit_helpers_demo"
    })
    
    # Sample candidate data
    candidates = [
        {"id": "c1", "name": "Alice", "rating": 4.5, "experience": 5, "price": 100},
        {"id": "c2", "name": "Bob", "rating": 3.8, "experience": 2, "price": 80},
        {"id": "c3", "name": "Charlie", "rating": 4.2, "experience": 7, "price": 120},
        {"id": "c4", "name": "Diana", "rating": 4.7, "experience": 8, "price": 150},
        {"id": "c5", "name": "Eve", "rating": 3.5, "experience": 1, "price": 60},
    ]
    
    print("📋 Starting with 5 candidates")
    print()
    
    # Step 1: Filter by Rating (using explicit filter_step helper)
    print("1️⃣ Filtering by Rating >= 4.0...")
    filtered = filter_step(
        xray,
        name="Filter by Rating",
        items=candidates,
        filter_fn=lambda c: c['rating'] >= 4.0,
        entity_id_key="id",
        reason_fn=lambda c, passed: (
            f"Rating {c['rating']} >= 4.0" if passed 
            else f"Rating {c['rating']} < 4.0 threshold"
        ),
        input_data={"min_rating": 4.0},
        rules=[{
            "rule_id": "min_rating",
            "description": "Minimum rating of 4.0 required",
            "operator": ">=",
            "value": 4.0,
            "source": "config"
        }]
    )
    print(f"   ✅ Filtered to {len(filtered)} candidates")
    print()
    
    # Step 2: Rank Candidates (using explicit rank_step helper)
    print("2️⃣ Ranking candidates by score...")
    ranked = rank_step(
        xray,
        name="Rank Candidates",
        items=filtered,
        rank_fn=lambda c: (c['rating'] * 0.5) + (c['experience'] * 0.3) + ((10 - c['price']/20) * 0.2),
        reverse=True,  # Higher score is better
        entity_id_key="id",
        reason_fn=lambda c, rank, score: (
            f"Ranked #{rank} - Score: {score:.2f} "
            f"(Rating: {c['rating']}, Exp: {c['experience']}y, Price: ${c['price']})"
        ),
        input_data={
            "criteria": "rating (50%) + experience (30%) + price (20%)"
        }
    )
    print(f"   ✅ Ranked {len(ranked)} candidates")
    print()
    
    # Step 3: Select Best (using explicit select_step helper)
    print("3️⃣ Selecting best candidate...")
    best = select_step(
        xray,
        name="Select Best Candidate",
        items=ranked,
        select_fn=lambda items: items[0],  # Already ranked, so first is best
        entity_id_key="id",
        reason_fn=lambda item: (
            f"Selected {item['name']} - Top ranked candidate "
            f"(Rating: {item['rating']}, Experience: {item['experience']}y, Price: ${item['price']})"
        ),
        input_data={"selection_criteria": "highest_score"}
    )
    print(f"   ✅ Selected: {best['name']}")
    print()
    
    # End execution
    xray.end_execution(status="completed")
    
    print("=" * 70)
    print("✅ Explicit Integration Helpers Demo Complete!")
    print("=" * 70)
    print(f"Execution ID: {xray.execution_id}")
    print(f"View in dashboard: http://localhost:3000")
    print("=" * 70)
    
    return best


if __name__ == "__main__":
    print()
    print("🚀 Running Explicit Integration Helpers Example")
    print()
    
    try:
        result = explicit_integration_example()
        print()
        print(f"📊 Final Result: {result['name']} (Rating: {result['rating']}, Price: ${result['price']})")
        print()
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

