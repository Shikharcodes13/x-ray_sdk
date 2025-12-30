"""
Example usage of the X-Ray SDK
This demonstrates how to instrument your code with execution tracking.
"""

import time
from sdk.xray import XRay

# Initialize X-Ray client
xray = XRay("candidate_ranking_run", api_url="http://localhost:8000")

# Start execution
xray.start_execution(metadata={
    "environment": "prod",
    "trigger": "api",
    "version": "1.0.0"
})

# Step 1: Keyword Generation
xray.start_step(
    name="Keyword Generation",
    step_type="transform",
    input_data={"query": "software engineer"},
    rules=[
        {
            "rule_id": "min_keywords",
            "description": "Generate at least 3 keywords",
            "operator": ">=",
            "value": 3,
            "source": "config"
        }
    ]
)

keywords = ["software engineer", "developer", "programmer", "coder"]
for i, keyword in enumerate(keywords):
    xray.record_evaluation(
        entity_id=f"keyword_{i}",
        value=keyword,
        passed=True,
        reason=f"Generated keyword: {keyword}"
    )

xray.end_step(output={
    "passed": len(keywords),
    "selected_ids": [f"keyword_{i}" for i in range(len(keywords))]
})

time.sleep(0.5)

# Step 2: Candidate Fetch
xray.start_step(
    name="Candidate Fetch",
    step_type="fetch",
    input_data={"keywords": keywords}
)

candidates = [
    {"id": "c1", "name": "Alice", "rating": 4.5, "skills": ["Python", "React"]},
    {"id": "c2", "name": "Bob", "rating": 3.8, "skills": ["Java", "Spring"]},
    {"id": "c3", "name": "Charlie", "rating": 4.2, "skills": ["Python", "Django"]},
    {"id": "c4", "name": "Diana", "rating": 4.7, "skills": ["React", "Node.js"]},
    {"id": "c5", "name": "Eve", "rating": 3.5, "skills": ["Vue", "PHP"]},
]

for candidate in candidates:
    xray.record_evaluation(
        entity_id=candidate["id"],
        value=candidate["rating"],
        passed=True,
        reason=f"Fetched candidate {candidate['name']} with rating {candidate['rating']}"
    )

xray.end_step(output={
    "passed": len(candidates),
    "selected_ids": [c["id"] for c in candidates]
})

time.sleep(0.5)

# Step 3: Filter Candidates
xray.start_step(
    name="Filter Candidates",
    step_type="filter",
    input_data={"min_rating": 4.0},
    rules=[
        {
            "rule_id": "min_rating",
            "description": "Minimum acceptable rating",
            "operator": ">=",
            "value": 4.0,
            "source": "config"
        }
    ]
)

min_rating = 4.0
filtered = []
for candidate in candidates:
    passed = candidate["rating"] >= min_rating
    xray.record_evaluation(
        entity_id=candidate["id"],
        value=candidate["rating"],
        passed=passed,
        reason=f"Rating {candidate['rating']} >= {min_rating}" if passed else f"Rating {candidate['rating']} < {min_rating}"
    )
    if passed:
        filtered.append(candidate)

xray.end_step(output={
    "passed": len(filtered),
    "failed": len(candidates) - len(filtered),
    "selected_ids": [c["id"] for c in filtered]
})

time.sleep(0.5)

# Step 4: Ranking
xray.start_step(
    name="Ranking",
    step_type="rank",
    input_data={"candidates": [c["id"] for c in filtered]}
)

# Sort by rating descending
ranked = sorted(filtered, key=lambda x: x["rating"], reverse=True)
for i, candidate in enumerate(ranked):
    xray.record_evaluation(
        entity_id=candidate["id"],
        value={"rank": i + 1, "rating": candidate["rating"]},
        passed=True,
        reason=f"Ranked #{i + 1} with rating {candidate['rating']}"
    )

xray.end_step(output={
    "passed": len(ranked),
    "selected_ids": [c["id"] for c in ranked],
    "data": {"top_3": [c["id"] for c in ranked[:3]]}
})

# End execution
xray.end_execution(status="completed")

print("Execution completed! Check the dashboard at http://localhost:3000")

