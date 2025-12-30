"""
Flight Evaluation Script using X-Ray SDK

This script demonstrates plug-and-play integration of X-Ray SDK to evaluate
flight options from a CSV file and find the best flight from Delhi to Mumbai
under ₹40,000.
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import sdk
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sdk import XRay, step


def parse_price(price_str: str) -> float:
    """Parse price string with commas to float."""
    if isinstance(price_str, str):
        # Remove commas and convert to float
        return float(price_str.replace(',', '').strip())
    return float(price_str)


def parse_duration(time_str: str) -> float:
    """Parse duration string (e.g., '02h 00m') to hours as float."""
    if not time_str or time_str.strip() == '':
        return 0.0
    
    # Extract hours and minutes
    hours_match = re.search(r'(\d+)h', time_str)
    minutes_match = re.search(r'(\d+)m', time_str)
    
    hours = float(hours_match.group(1)) if hours_match else 0.0
    minutes = float(minutes_match.group(1)) if minutes_match else 0.0
    
    return hours + (minutes / 60.0)


def is_non_stop(stop_str: str) -> bool:
    """Check if flight is non-stop."""
    if not stop_str:
        return False
    return 'non-stop' in stop_str.lower().strip()


def load_flights_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    Load and parse flights from CSV file.
    
    Expected CSV columns:
    date, airline, ch_code, num_code, dep_time, from, time_taken, stop, arr_time, to, price
    """
    flights = []
    
    # Required columns in the CSV
    required_columns = ['date', 'airline', 'ch_code', 'num_code', 'dep_time', 
                       'from', 'time_taken', 'stop', 'arr_time', 'to', 'price']
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Validate that all required columns are present
        if not reader.fieldnames:
            raise ValueError("CSV file appears to be empty or has no header row")
        
        # Strip BOM and whitespace from fieldnames (in case of encoding issues)
        reader.fieldnames = [name.strip().lstrip('\ufeff') for name in reader.fieldnames]
        
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"CSV file is missing required columns: {missing_columns}. "
                           f"Found columns: {list(reader.fieldnames)}")
        
        for row in reader:
            try:
                flight = {
                    'flight_id': f"{row['ch_code']}{row['num_code']}",
                    'date': row['date'],
                    'airline': row['airline'],
                    'code': row['ch_code'],
                    'number': row['num_code'],
                    'departure_time': row['dep_time'],
                    'from': row['from'].strip(),
                    'time_taken': row['time_taken'],
                    'duration_hours': parse_duration(row['time_taken']),
                    'stop': row['stop'].strip() if row['stop'] else '',
                    'is_non_stop': is_non_stop(row['stop']),
                    'arrival_time': row['arr_time'],
                    'to': row['to'].strip(),
                    'price_str': row['price'],
                    'price': parse_price(row['price'])
                }
                flights.append(flight)
            except KeyError as e:
                # Skip rows with missing required columns
                print(f"Warning: Skipping row due to missing column: {e}")
                continue
            except Exception as e:
                # Skip malformed rows
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    return flights


def calculate_score(flight: Dict[str, Any]) -> float:
    """
    Calculate a score for ranking flights.
    Lower score is better (for sorting).
    
    Scoring criteria:
    - Prefer non-stop flights
    - Prefer lower price
    - Prefer shorter duration
    """
    score = 0.0
    
    # Price component (normalized, lower is better)
    # Assuming max price is around 100k for normalization
    price_component = flight['price'] / 100000.0
    score += price_component * 0.5  # 50% weight on price
    
    # Duration component (normalized, lower is better)
    # Assuming max duration is 30 hours for normalization
    duration_component = flight['duration_hours'] / 30.0
    score += duration_component * 0.3  # 30% weight on duration
    
    # Non-stop bonus (20% weight)
    if not flight['is_non_stop']:
        score += 0.2  # Penalty for stops
    
    return score


def evaluate_flights():
    """Main function to evaluate flights using X-Ray SDK."""
    
    # Initialize X-Ray
    xray = XRay("flight_evaluation_delhi_mumbai", api_url="http://localhost:8000")
    
    # Start execution
    xray.start_execution(metadata={
        "environment": "production",
        "task": "find_best_flight",
        "route": "Delhi to Mumbai",
        "budget": 40000,
        "date": datetime.now().isoformat()
    })
    
    # Step 1: Load Flight Data from CSV
    with step(xray, "Load Flight Data", step_type="load",
              input_data={"csv_file": "business.csv"}) as step_ctx:
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "business.csv")
        flights = load_flights_from_csv(csv_path)
        
        # Record each flight as loaded
        for flight in flights:
            step_ctx.log_evaluation(
                entity_id=flight['flight_id'],
                value={
                    "from": flight['from'],
                    "to": flight['to'],
                    "price": flight['price'],
                    "airline": flight['airline']
                },
                passed=True,
                reason=f"Loaded flight {flight['flight_id']} from CSV"
            )
        
        step_ctx.set_output({
            "total_flights_loaded": len(flights),
            "sample_flights": [f["flight_id"] for f in flights[:5]]
        })
    
    print(f"✅ Loaded {len(flights)} flights from CSV")
    
    # Step 2: Filter by Route (Delhi to Mumbai)
    with step(xray, "Filter by Route", step_type="filter",
              input_data={
                  "origin": "Delhi",
                  "destination": "Mumbai"
              },
              rules=[{
                  "rule_id": "route_match",
                  "description": "Flight must be from Delhi to Mumbai",
                  "operator": "==",
                  "value": True,
                  "source": "config"
              }]) as step_ctx:
        
        route_filtered = []
        for flight in flights:
            route_match = (flight['from'].lower() == 'delhi' and 
                          flight['to'].lower() == 'mumbai')
            
            step_ctx.evaluate(
                entity_id=flight['flight_id'],
                value=f"{flight['from']} → {flight['to']}",
                condition=route_match,
                reason=f"Route check: {flight['from']} → {flight['to']}"
            )
            
            if route_match:
                route_filtered.append(flight)
        
        step_ctx.set_output({
            "filtered_count": len(route_filtered),
            "passed": len(route_filtered),
            "failed": len(flights) - len(route_filtered)
        })
    
    print(f"✅ Filtered to {len(route_filtered)} flights on Delhi → Mumbai route")
    
    # Step 3: Filter by Budget (Under ₹40,000)
    with step(xray, "Filter by Budget", step_type="filter",
              input_data={"max_price": 40000},
              rules=[{
                  "rule_id": "budget_constraint",
                  "description": "Flight price must be under Rs. 40,000",
                  "operator": "<=",
                  "value": 40000,
                  "source": "config"
              }]) as step_ctx:
        
        budget_filtered = []
        for flight in route_filtered:
            within_budget = flight['price'] <= 40000
            
            step_ctx.evaluate(
                entity_id=flight['flight_id'],
                value=flight['price'],
                condition=within_budget,
                reason=f"Price Rs. {flight['price']:,.0f} {'<=' if within_budget else '>'} Rs. 40,000"
            )
            
            if within_budget:
                budget_filtered.append(flight)
        
        step_ctx.set_output({
            "filtered_count": len(budget_filtered),
            "passed": len(budget_filtered),
            "failed": len(route_filtered) - len(budget_filtered),
            "max_price_found": max([f['price'] for f in budget_filtered]) if budget_filtered else 0
        })
    
    print(f"✅ Filtered to {len(budget_filtered)} flights under ₹40,000")
    
    if not budget_filtered:
        print("❌ No flights found within budget!")
        xray.end_execution(status="completed")
        return None
    
    # Step 4: Rank Flights
    with step(xray, "Rank Flights", step_type="rank",
              input_data={
                  "criteria": "price + duration + non-stop preference",
                  "candidates_count": len(budget_filtered)
              }) as step_ctx:
        
        # Calculate scores and sort
        for flight in budget_filtered:
            flight['score'] = calculate_score(flight)
        
        ranked = sorted(budget_filtered, key=lambda x: x['score'])
        
        # Record rankings
        for i, flight in enumerate(ranked):
            step_ctx.log_evaluation(
                entity_id=flight['flight_id'],
                value={
                    "rank": i + 1,
                    "score": round(flight['score'], 4),
                    "price": flight['price'],
                    "duration_hours": round(flight['duration_hours'], 2),
                    "is_non_stop": flight['is_non_stop']
                },
                passed=True,
                reason=f"Ranked #{i + 1} - Score: {flight['score']:.4f}, "
                      f"Price: ₹{flight['price']:,.0f}, "
                      f"Duration: {flight['duration_hours']:.1f}h, "
                      f"Non-stop: {flight['is_non_stop']}"
            )
        
        step_ctx.set_output({
            "ranked_count": len(ranked),
            "top_3_ids": [f['flight_id'] for f in ranked[:3]],
            "top_3_prices": [f['price'] for f in ranked[:3]]
        })
    
    print(f"✅ Ranked {len(ranked)} flights")
    
    # Step 5: Select Best Option
    with step(xray, "Select Best Flight", step_type="select",
              input_data={"selection_criteria": "lowest score (best price + duration)"}) as step_ctx:
        
        best_flight = ranked[0]
        
        step_ctx.log_evaluation(
            entity_id=best_flight['flight_id'],
            value=best_flight,
            passed=True,
            reason=f"Selected as best option - Rank #1, "
                  f"Price: Rs. {best_flight['price']:,.0f}, "
                  f"Duration: {best_flight['duration_hours']:.1f}h, "
                  f"Non-stop: {best_flight['is_non_stop']}, "
                  f"Airline: {best_flight['airline']}"
        )
        
        step_ctx.set_output({
            "selected_flight_id": best_flight['flight_id'],
            "selected_airline": best_flight['airline'],
            "selected_price": best_flight['price'],
            "selected_duration": best_flight['duration_hours'],
            "selected_departure": best_flight['departure_time'],
            "selected_arrival": best_flight['arrival_time'],
            "is_non_stop": best_flight['is_non_stop'],
            "rank": 1,
            "score": best_flight['score']
        })
    
    # End execution
    xray.end_execution(status="completed")
    
    # Print results
    print("\n" + "="*60)
    print("🎯 BEST FLIGHT SELECTED")
    print("="*60)
    print(f"Flight ID: {best_flight['flight_id']}")
    print(f"Airline: {best_flight['airline']}")
    print(f"Route: {best_flight['from']} → {best_flight['to']}")
    print(f"Price: Rs. {best_flight['price']:,.0f}")
    print(f"Duration: {best_flight['duration_hours']:.1f} hours ({best_flight['time_taken']})")
    print(f"Departure: {best_flight['departure_time']}")
    print(f"Arrival: {best_flight['arrival_time']}")
    print(f"Non-stop: {'Yes' if best_flight['is_non_stop'] else 'No'}")
    print(f"Rank: #1 (Score: {best_flight['score']:.4f})")
    print("="*60)
    print(f"\n✅ Execution completed! Check dashboard at http://localhost:3000")
    print(f"   Execution ID: {xray.execution_id}")
    
    return best_flight


if __name__ == "__main__":
    print("="*60)
    print("Flight Evaluation: Delhi to Mumbai (Under Rs. 40,000)")
    print("="*60)
    print()
    
    try:
        best_flight = evaluate_flights()
        if best_flight:
            print("\n✅ Successfully found best flight option!")
        else:
            print("\n❌ No suitable flights found.")
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

