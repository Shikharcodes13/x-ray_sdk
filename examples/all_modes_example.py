"""
Complete Example: All 3 Integration Modes

This example demonstrates all three X-Ray integration modes working together
in a realistic candidate evaluation pipeline:

1. Direct Code Integration - Custom data loading and validation
2. Adapter Mode - Wrapping existing business logic functions
3. Data-Driven Mode - Configurable filtering and ranking pipeline
"""

import os
import sys
from typing import List, Dict, Any

# Add parent directory to path to import sdk
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sdk import XRay, step, trace_function, StepRunner


# ============================================================================
# EXISTING BUSINESS LOGIC FUNCTIONS (No X-Ray code!)
# ============================================================================
# These are your normal business functions - they don't know about X-Ray

def calculate_score(candidate: Dict[str, Any]) -> float:
    """Calculate overall score for a candidate."""
    rating = candidate.get('rating', 0)
    experience = candidate.get('experience_years', 0)
    skills_count = len(candidate.get('skills', []))
    
    # Simple scoring: rating (50%) + experience (30%) + skills (20%)
    score = (rating * 0.5) + (min(experience, 10) * 0.3) + (min(skills_count, 10) * 0.2)
    return round(score, 2)


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank candidates by their calculated score."""
    scored = []
    for candidate in candidates:
        candidate['score'] = calculate_score(candidate)
        scored.append(candidate)
    
    return sorted(scored, key=lambda x: x['score'], reverse=True)


def filter_by_minimum_rating(candidates: List[Dict[str, Any]], min_rating: float) -> List[Dict[str, Any]]:
    """Filter candidates by minimum rating."""
    return [c for c in candidates if c.get('rating', 0) >= min_rating]


# ============================================================================
# MAIN EXAMPLE: Using All 3 Modes
# ============================================================================

def evaluate_candidates_all_modes():
    """
    Complete example using all three integration modes:
    
    MODE 1 (Direct): Load and validate candidate data
    MODE 2 (Adapter): Wrap existing filter/rank functions
    MODE 3 (Data-Driven): Execute configurable pipeline steps
    """
    
    print("=" * 70)
    print("Candidate Evaluation Pipeline - All 3 Integration Modes")
    print("=" * 70)
    print()
    
    # Initialize X-Ray
    xray = XRay("candidate_evaluation_all_modes", api_url="http://localhost:8000")
    xray.start_execution(metadata={
        "environment": "production",
        "task": "evaluate_candidates",
        "pipeline": "multi_mode_demo"
    })
    
    # ========================================================================
    # MODE 1: DIRECT CODE INTEGRATION
    # ========================================================================
    # Use this for custom logic, data loading, validation, etc.
    
    print("📝 MODE 1: Direct Code Integration - Loading & Validating Data")
    print("-" * 70)
    
    with step(xray, "Load Candidate Data", step_type="load",
              input_data={"source": "internal_database"}) as step_ctx:
        
        # Simulate loading candidate data
        raw_candidates = [
            {"id": "c1", "name": "Alice", "rating": 4.5, "experience_years": 5, "skills": ["Python", "ML", "SQL"]},
            {"id": "c2", "name": "Bob", "rating": 3.8, "experience_years": 2, "skills": ["Java", "Spring"]},
            {"id": "c3", "name": "Charlie", "rating": 4.2, "experience_years": 7, "skills": ["Python", "Django", "PostgreSQL", "Redis"]},
            {"id": "c4", "name": "Diana", "rating": 4.7, "experience_years": 8, "skills": ["Python", "ML", "TensorFlow", "Kubernetes"]},
            {"id": "c5", "name": "Eve", "rating": 3.5, "experience_years": 1, "skills": ["JavaScript"]},
        ]
        
        # Validate each candidate
        validated_candidates = []
        for candidate in raw_candidates:
            # Custom validation logic
            has_required_fields = all(key in candidate for key in ['id', 'name', 'rating'])
            has_valid_rating = 0 <= candidate.get('rating', 0) <= 5
            
            is_valid = has_required_fields and has_valid_rating
            
            # Record evaluation (MODE 1: manual tracking)
            step_ctx.evaluate(
                entity_id=candidate['id'],
                value={
                    "name": candidate['name'],
                    "rating": candidate.get('rating', 0),
                    "has_required_fields": has_required_fields
                },
                condition=is_valid,
                reason=f"Validation: {'All checks passed' if is_valid else 'Missing fields or invalid rating'}"
            )
            
            if is_valid:
                validated_candidates.append(candidate)
        
        step_ctx.set_output({
            "total_loaded": len(raw_candidates),
            "validated_count": len(validated_candidates),
            "invalid_count": len(raw_candidates) - len(validated_candidates)
        })
        
        print(f"   ✓ Loaded {len(raw_candidates)} candidates")
        print(f"   ✓ Validated {len(validated_candidates)} candidates")
    
    print()
    
    # ========================================================================
    # MODE 2: ADAPTER MODE - Wrap Existing Functions
    # ========================================================================
    # Use this to track existing functions without modifying them
    
    print("🔌 MODE 2: Adapter Mode - Wrapping Existing Functions")
    print("-" * 70)
    
    # Wrap existing functions with X-Ray decorators
    @trace_function(xray, step_type="filter")
    def traced_filter_by_rating(candidates, min_rating):
        """Wrapped version of filter_by_minimum_rating - automatically tracked!"""
        return filter_by_minimum_rating(candidates, min_rating)
    
    @trace_function(xray, step_type="rank")
    def traced_rank_candidates(candidates):
        """Wrapped version of rank_candidates - automatically tracked!"""
        return rank_candidates(candidates)
    
    # Use wrapped functions - X-Ray automatically creates steps and tracks them
    print("   → Filtering candidates with rating >= 4.0...")
    filtered = traced_filter_by_rating(validated_candidates, min_rating=4.0)
    print(f"   ✓ Filtered to {len(filtered)} candidates")
    
    print("   → Ranking candidates by score...")
    ranked = traced_rank_candidates(filtered)
    print(f"   ✓ Ranked {len(ranked)} candidates")
    print()
    
    # ========================================================================
    # MODE 3: DATA-DRIVEN MODE - Configuration-Based Execution
    # ========================================================================
    # Use this for configurable pipelines, external configs, etc.
    
    print("⚙️  MODE 3: Data-Driven Mode - Configuration-Based Pipeline")
    print("-" * 70)
    
    # Create step runner
    runner = StepRunner(xray)
    
    # Register handlers for different step types
    def skill_filter_handler(input_data, rules):
        """Handler for filtering by required skills."""
        candidates = input_data.get("candidates", [])
        required_skills = input_data.get("required_skills", [])
        
        filtered = []
        evaluations = []
        
        for candidate in candidates:
            candidate_skills = set(candidate.get('skills', []))
            required_skills_set = set(required_skills)
            
            has_all_skills = required_skills_set.issubset(candidate_skills)
            
            evaluations.append({
                "entity_id": candidate["id"],
                "value": {
                    "candidate_skills": list(candidate_skills),
                    "required_skills": list(required_skills_set),
                    "match": has_all_skills
                },
                "passed": has_all_skills,
                "reason": f"Has all required skills: {has_all_skills}"
            })
            
            if has_all_skills:
                filtered.append(candidate)
        
        return {
            "filtered_count": len(filtered),
            "filtered_ids": [c["id"] for c in filtered],
            "evaluations": evaluations  # SDK automatically logs these
        }
    
    def experience_filter_handler(input_data, rules):
        """Handler for filtering by minimum experience."""
        candidates = input_data.get("candidates", [])
        min_experience = input_data.get("min_experience", 0)
        
        filtered = []
        evaluations = []
        
        for candidate in candidates:
            experience = candidate.get('experience_years', 0)
            meets_requirement = experience >= min_experience
            
            evaluations.append({
                "entity_id": candidate["id"],
                "value": experience,
                "passed": meets_requirement,
                "reason": f"Experience: {experience} years {'>=' if meets_requirement else '<'} {min_experience} years"
            })
            
            if meets_requirement:
                filtered.append(candidate)
        
        return {
            "filtered_count": len(filtered),
            "filtered_ids": [c["id"] for c in filtered],
            "evaluations": evaluations
        }
    
    def top_n_select_handler(input_data, rules):
        """Handler for selecting top N candidates."""
        candidates = input_data.get("candidates", [])
        top_n = input_data.get("top_n", 3)
        
        # Assume candidates are already ranked
        selected = candidates[:top_n]
        
        evaluations = []
        for i, candidate in enumerate(selected):
            evaluations.append({
                "entity_id": candidate["id"],
                "value": {
                    "rank": i + 1,
                    "score": candidate.get('score', 0),
                    "name": candidate.get('name', '')
                },
                "passed": True,
                "reason": f"Selected as top {i + 1} candidate (score: {candidate.get('score', 0)})"
            })
        
        return {
            "selected_count": len(selected),
            "selected_ids": [c["id"] for c in selected],
            "evaluations": evaluations
        }
    
    # Register handlers
    runner.register_handler("skill_filter", skill_filter_handler)
    runner.register_handler("experience_filter", experience_filter_handler)
    runner.register_handler("top_n_select", top_n_select_handler)
    
    # Define pipeline as configuration (could come from JSON/YAML file!)
    pipeline_config = [
        {
            "name": "Filter by Required Skills",
            "type": "skill_filter",
            "input": {
                "candidates": ranked,  # Use output from Mode 2
                "required_skills": ["Python", "ML"]
            },
            "rules": [
                {
                    "rule_id": "must_have_python_ml",
                    "description": "Candidate must have Python and ML skills",
                    "operator": "contains",
                    "value": ["Python", "ML"],
                    "source": "config"
                }
            ]
        },
        {
            "name": "Filter by Minimum Experience",
            "type": "experience_filter",
            "input": {
                "candidates": ranked,  # Could use output from previous step
                "min_experience": 5
            },
            "rules": [
                {
                    "rule_id": "min_5_years",
                    "description": "Minimum 5 years of experience required",
                    "operator": ">=",
                    "value": 5,
                    "source": "config"
                }
            ]
        },
        {
            "name": "Select Top 3 Candidates",
            "type": "top_n_select",
            "input": {
                "candidates": ranked,
                "top_n": 3
            },
            "rules": []
        }
    ]
    
    # Execute pipeline from configuration
    print("   → Executing pipeline from configuration...")
    outputs = runner.execute_pipeline(pipeline_config)
    
    print(f"   ✓ Executed {len(outputs)} steps from configuration")
    print(f"   ✓ Skill filter: {outputs[0].get('filtered_count', 0)} candidates passed")
    print(f"   ✓ Experience filter: {outputs[1].get('filtered_count', 0)} candidates passed")
    print(f"   ✓ Top 3 selected: {outputs[2].get('selected_count', 0)} candidates")
    print()
    
    # ========================================================================
    # Final Step: Direct Integration for Summary
    # ========================================================================
    
    print("📊 Final Summary - Direct Integration")
    print("-" * 70)
    
    with step(xray, "Generate Final Report", step_type="report") as step_ctx:
        top_candidates = outputs[2].get('selected_ids', [])
        
        final_report = {
            "total_candidates_processed": len(validated_candidates),
            "after_rating_filter": len(filtered),
            "after_skill_filter": outputs[0].get('filtered_count', 0),
            "after_experience_filter": outputs[1].get('filtered_count', 0),
            "final_selected": len(top_candidates),
            "selected_candidate_ids": top_candidates
        }
        
        # Log each selected candidate
        for candidate_id in top_candidates:
            candidate = next((c for c in ranked if c['id'] == candidate_id), None)
            if candidate:
                step_ctx.log_evaluation(
                    entity_id=candidate_id,
                    value={
                        "name": candidate['name'],
                        "score": candidate.get('score', 0),
                        "rating": candidate.get('rating', 0)
                    },
                    passed=True,
                    reason=f"Final selection: {candidate['name']} (Score: {candidate.get('score', 0)})"
                )
        
        step_ctx.set_output(final_report)
        
        print(f"   ✓ Generated final report")
        print(f"   ✓ Selected {len(top_candidates)} top candidates")
    
    # End execution
    xray.end_execution(status="completed")
    
    print()
    print("=" * 70)
    print("✅ All 3 Integration Modes Completed Successfully!")
    print("=" * 70)
    print(f"Execution ID: {xray.execution_id}")
    print(f"View in dashboard: http://localhost:3000")
    print("=" * 70)
    
    return {
        "execution_id": xray.execution_id,
        "validated": len(validated_candidates),
        "filtered": len(filtered),
        "ranked": len(ranked),
        "selected": top_candidates
    }


if __name__ == "__main__":
    print()
    print("🚀 Running Complete Example: All 3 Integration Modes")
    print()
    
    try:
        result = evaluate_candidates_all_modes()
        print()
        print("📋 Summary:")
        print(f"   - Validated candidates: {result['validated']}")
        print(f"   - After rating filter: {result['filtered']}")
        print(f"   - Ranked candidates: {result['ranked']}")
        print(f"   - Final selected: {len(result['selected'])}")
        print()
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

