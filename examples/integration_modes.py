"""
X-Ray SDK Integration Modes

This file demonstrates the three ways to integrate X-Ray into any system:

1. Direct Code Integration - Manual instrumentation
2. Adapter Mode - Wrap existing functions with decorators
3. Data-Driven Mode - Execute steps from configuration
"""

import time
from sdk import XRay, step, trace_function, StepRunner


# ============================================================================
# MODE 1: Direct Code Integration
# ============================================================================
# For Python users writing code directly. You manually instrument your logic.

def mode1_direct_integration():
    """Example of direct code integration."""
    xray = XRay("direct_integration_example", api_url="http://localhost:8000")
    xray.start_execution(metadata={"mode": "direct", "environment": "dev"})
    
    # Step 1: Transform data
    with step(xray, "Transform Data", step_type="transform", 
              input_data={"source": "raw_data.csv"}) as step_ctx:
        
        # Your business logic here
        data = [1, 2, 3, 4, 5]
        transformed = [x * 2 for x in data]
        
        # Record evaluations
        for i, value in enumerate(transformed):
            step_ctx.log_evaluation(
                entity_id=f"item_{i}",
                value=value,
                passed=True,
                reason=f"Transformed {data[i]} to {value}"
            )
        
        step_ctx.set_output({"transformed_count": len(transformed), "data": transformed})
    
    # Step 2: Filter data
    with step(xray, "Filter Data", step_type="filter",
              input_data={"min_value": 6}) as step_ctx:
        
        filtered = [x for x in transformed if x >= 6]
        
        for i, value in enumerate(transformed):
            passed = value >= 6
            step_ctx.evaluate(
                entity_id=f"item_{i}",
                value=value,
                condition=passed,
                reason=f"Value {value} {'>=' if passed else '<'} 6"
            )
        
        step_ctx.set_output({"filtered_count": len(filtered), "data": filtered})
    
    xray.end_execution(status="completed")
    print("✅ Mode 1: Direct integration completed")


# ============================================================================
# MODE 2: Adapter Mode - Wrap Existing Functions
# ============================================================================
# Wrap existing functions without modifying their code.

def filter_candidates(candidates, min_rating):
    """
    Existing function - no X-Ray code here!
    This is your normal business logic.
    """
    return [c for c in candidates if c.get('rating', 0) >= min_rating]


def rank_candidates(candidates):
    """Another existing function."""
    return sorted(candidates, key=lambda x: x.get('rating', 0), reverse=True)


def mode2_adapter_mode():
    """Example of adapter mode - wrapping existing functions."""
    xray = XRay("adapter_mode_example", api_url="http://localhost:8000")
    xray.start_execution(metadata={"mode": "adapter", "environment": "dev"})
    
    # Wrap functions with X-Ray tracing
    @trace_function(xray, step_type="filter")
    def traced_filter(candidates, min_rating):
        return filter_candidates(candidates, min_rating)
    
    @trace_function(xray, step_type="rank")
    def traced_rank(candidates):
        return rank_candidates(candidates)
    
    # Use wrapped functions - X-Ray automatically tracks them
    candidates = [
        {"id": "c1", "name": "Alice", "rating": 4.5},
        {"id": "c2", "name": "Bob", "rating": 3.8},
        {"id": "c3", "name": "Charlie", "rating": 4.2},
    ]
    
    filtered = traced_filter(candidates, min_rating=4.0)
    ranked = traced_rank(filtered)
    
    xray.end_execution(status="completed")
    print("✅ Mode 2: Adapter mode completed")
    return ranked


# ============================================================================
# MODE 3: Data-Driven Mode - Configuration-Based Execution
# ============================================================================
# Execute steps from configuration (JSON, YAML, etc.)

def mode3_data_driven():
    """Example of data-driven mode - execute from configuration."""
    xray = XRay("data_driven_example", api_url="http://localhost:8000")
    xray.start_execution(metadata={"mode": "data_driven", "environment": "dev"})
    
    # Create step runner
    runner = StepRunner(xray)
    
    # Register handlers for different step types
    def filter_handler(input_data, rules):
        """Handler for filter steps."""
        candidates = input_data.get("candidates", [])
        min_rating = input_data.get("min_rating", 0)
        
        filtered = []
        evaluations = []
        
        for candidate in candidates:
            passed = candidate.get("rating", 0) >= min_rating
            evaluations.append({
                "entity_id": candidate["id"],
                "value": candidate.get("rating", 0),
                "passed": passed,
                "reason": f"Rating {candidate.get('rating', 0)} >= {min_rating}" if passed else f"Rating {candidate.get('rating', 0)} < {min_rating}"
            })
            if passed:
                filtered.append(candidate)
        
        return {
            "filtered_count": len(filtered),
            "filtered_ids": [c["id"] for c in filtered],
            "evaluations": evaluations
        }
    
    def rank_handler(input_data, rules):
        """Handler for rank steps."""
        candidates = input_data.get("candidates", [])
        ranked = sorted(candidates, key=lambda x: x.get("rating", 0), reverse=True)
        
        evaluations = []
        for i, candidate in enumerate(ranked):
            evaluations.append({
                "entity_id": candidate["id"],
                "value": {"rank": i + 1, "rating": candidate.get("rating", 0)},
                "passed": True,
                "reason": f"Ranked #{i + 1} with rating {candidate.get('rating', 0)}"
            })
        
        return {
            "ranked_count": len(ranked),
            "ranked_ids": [c["id"] for c in ranked],
            "evaluations": evaluations
        }
    
    def transform_handler(input_data, rules):
        """Handler for transform steps."""
        data = input_data.get("data", [])
        multiplier = input_data.get("multiplier", 1)
        
        transformed = [x * multiplier for x in data]
        evaluations = []
        
        for i, (original, new_value) in enumerate(zip(data, transformed)):
            evaluations.append({
                "entity_id": f"item_{i}",
                "value": new_value,
                "passed": True,
                "reason": f"Transformed {original} to {new_value}"
            })
        
        return {
            "transformed_count": len(transformed),
            "data": transformed,
            "evaluations": evaluations
        }
    
    # Register handlers
    runner.register_handler("filter", filter_handler)
    runner.register_handler("rank", rank_handler)
    runner.register_handler("transform", transform_handler)
    
    # Define pipeline as configuration
    pipeline_config = [
        {
            "name": "Transform Data",
            "type": "transform",
            "input": {
                "data": [1, 2, 3, 4, 5],
                "multiplier": 2
            },
            "rules": []
        },
        {
            "name": "Filter Candidates",
            "type": "filter",
            "input": {
                "candidates": [
                    {"id": "c1", "name": "Alice", "rating": 4.5},
                    {"id": "c2", "name": "Bob", "rating": 3.8},
                    {"id": "c3", "name": "Charlie", "rating": 4.2},
                    {"id": "c4", "name": "Diana", "rating": 4.7},
                ],
                "min_rating": 4.0
            },
            "rules": [
                {
                    "rule_id": "min_rating",
                    "description": "Minimum acceptable rating",
                    "operator": ">=",
                    "value": 4.0,
                    "source": "config"
                }
            ]
        },
        {
            "name": "Rank Candidates",
            "type": "rank",
            "input": {
                "candidates": [
                    {"id": "c1", "name": "Alice", "rating": 4.5},
                    {"id": "c3", "name": "Charlie", "rating": 4.2},
                    {"id": "c4", "name": "Diana", "rating": 4.7},
                ]
            },
            "rules": []
        }
    ]
    
    # Execute pipeline from configuration
    outputs = runner.execute_pipeline(pipeline_config)
    
    xray.end_execution(status="completed")
    print("✅ Mode 3: Data-driven mode completed")
    print(f"   Executed {len(outputs)} steps from configuration")
    return outputs


# ============================================================================
# HYBRID: Combining Modes
# ============================================================================

def hybrid_example():
    """Example combining multiple modes."""
    xray = XRay("hybrid_example", api_url="http://localhost:8000")
    xray.start_execution(metadata={"mode": "hybrid", "environment": "dev"})
    
    # Use direct integration for custom logic
    with step(xray, "Custom Processing", step_type="transform") as step_ctx:
        data = [1, 2, 3]
        step_ctx.set_output({"processed": len(data)})
    
    # Use adapter mode for existing functions
    @trace_function(xray, step_type="filter")
    def quick_filter(items, threshold):
        return [x for x in items if x > threshold]
    
    result = quick_filter([1, 2, 3, 4, 5], threshold=3)
    
    # Use data-driven for configurable steps
    runner = StepRunner(xray)
    runner.register_handler("transform", lambda input_data, rules: {"result": input_data.get("data", [])})
    
    runner.execute_step({
        "name": "Final Step",
        "type": "transform",
        "input": {"data": result}
    })
    
    xray.end_execution(status="completed")
    print("✅ Hybrid mode completed")


if __name__ == "__main__":
    print("=" * 60)
    print("X-Ray SDK Integration Modes Demo")
    print("=" * 60)
    print()
    
    print("Mode 1: Direct Code Integration")
    print("-" * 60)
    mode1_direct_integration()
    print()
    
    time.sleep(1)
    
    print("Mode 2: Adapter Mode (Function Wrapping)")
    print("-" * 60)
    mode2_adapter_mode()
    print()
    
    time.sleep(1)
    
    print("Mode 3: Data-Driven Mode (Configuration-Based)")
    print("-" * 60)
    mode3_data_driven()
    print()
    
    time.sleep(1)
    
    print("Hybrid: Combining All Modes")
    print("-" * 60)
    hybrid_example()
    print()
    
    print("=" * 60)
    print("All modes completed! Check the dashboard at http://localhost:3000")
    print("=" * 60)

