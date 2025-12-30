"""
X-Ray SDK Integration Helpers

Convenience functions for common integration patterns.
These are optional helpers that make common use cases easier while
maintaining the general-purpose nature of the SDK.
"""

from typing import List, Dict, Any, Callable, Optional
from .xray import XRay, step, StepContext


def filter_step(
    xray: XRay,
    name: str,
    items: List[Dict[str, Any]],
    filter_fn: Callable[[Dict[str, Any]], bool],
    entity_id_key: str = "id",
    reason_fn: Optional[Callable[[Dict[str, Any], bool], str]] = None,
    input_data: Optional[Dict[str, Any]] = None,
    rules: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for filter steps.
    
    Automatically creates a filter step, evaluates each item, and returns filtered results.
    
    Args:
        xray: XRay instance
        name: Step name
        items: List of items to filter
        filter_fn: Function that takes an item and returns True if it passes the filter
        entity_id_key: Key to use for entity_id (default: "id")
        reason_fn: Optional function to generate reason string (item, passed) -> str
        input_data: Additional input data for the step
        rules: Optional rule definitions
    
    Returns:
        List of items that passed the filter
    
    Example:
        >>> filtered = filter_step(
        ...     xray, "Filter by Rating",
        ...     candidates,
        ...     filter_fn=lambda c: c['rating'] >= 4.0,
        ...     reason_fn=lambda c, passed: f"Rating {c['rating']} {'>=' if passed else '<'} 4.0"
        ... )
    """
    filtered = []
    
    with step(xray, name, step_type="filter", input_data=input_data, rules=rules) as step_ctx:
        for item in items:
            entity_id = item.get(entity_id_key, str(item))
            passed = filter_fn(item)
            
            if reason_fn:
                reason = reason_fn(item, passed)
            else:
                reason = f"Filter {'passed' if passed else 'failed'}"
            
            step_ctx.evaluate(
                entity_id=entity_id,
                value=item,
                condition=passed,
                reason=reason
            )
            
            if passed:
                filtered.append(item)
        
        step_ctx.set_output({
            "total_evaluated": len(items),
            "passed": len(filtered),
            "failed": len(items) - len(filtered)
        })
    
    return filtered


def rank_step(
    xray: XRay,
    name: str,
    items: List[Dict[str, Any]],
    rank_fn: Callable[[Dict[str, Any]], float],
    reverse: bool = True,
    entity_id_key: str = "id",
    reason_fn: Optional[Callable[[Dict[str, Any], int, float], str]] = None,
    input_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for ranking steps.
    
    Automatically creates a ranking step, scores each item, and returns ranked results.
    
    Args:
        xray: XRay instance
        name: Step name
        items: List of items to rank
        rank_fn: Function that takes an item and returns a score (higher is better if reverse=True)
        reverse: If True, higher scores rank first (default: True)
        entity_id_key: Key to use for entity_id (default: "id")
        reason_fn: Optional function to generate reason string (item, rank, score) -> str
        input_data: Additional input data for the step
    
    Returns:
        List of items sorted by score
    
    Example:
        >>> ranked = rank_step(
        ...     xray, "Rank Candidates",
        ...     candidates,
        ...     rank_fn=lambda c: c['rating'] * 0.5 + c['experience'] * 0.3,
        ...     reason_fn=lambda c, rank, score: f"Ranked #{rank} with score {score:.2f}"
        ... )
    """
    # Score all items
    scored_items = []
    for item in items:
        score = rank_fn(item)
        item_copy = item.copy()
        item_copy['_xray_score'] = score
        scored_items.append(item_copy)
    
    # Sort by score
    ranked = sorted(scored_items, key=lambda x: x['_xray_score'], reverse=reverse)
    
    with step(xray, name, step_type="rank", input_data=input_data) as step_ctx:
        for i, item in enumerate(ranked):
            entity_id = item.get(entity_id_key, str(item))
            score = item['_xray_score']
            rank = i + 1
            
            if reason_fn:
                reason = reason_fn(item, rank, score)
            else:
                reason = f"Ranked #{rank} with score {score:.2f}"
            
            step_ctx.log_evaluation(
                entity_id=entity_id,
                value={"rank": rank, "score": score},
                passed=True,
                reason=reason
            )
        
        step_ctx.set_output({
            "ranked_count": len(ranked),
            "top_3_ids": [item.get(entity_id_key, str(item)) for item in ranked[:3]]
        })
    
    # Remove temporary score field
    for item in ranked:
        item.pop('_xray_score', None)
    
    return ranked


def transform_step(
    xray: XRay,
    name: str,
    items: List[Dict[str, Any]],
    transform_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    entity_id_key: str = "id",
    reason_fn: Optional[Callable[[Dict[str, Any], Dict[str, Any]], str]] = None,
    input_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for transform steps.
    
    Automatically creates a transform step, transforms each item, and returns results.
    
    Args:
        xray: XRay instance
        name: Step name
        items: List of items to transform
        transform_fn: Function that takes an item and returns transformed item
        entity_id_key: Key to use for entity_id (default: "id")
        reason_fn: Optional function to generate reason string (original, transformed) -> str
        input_data: Additional input data for the step
    
    Returns:
        List of transformed items
    
    Example:
        >>> transformed = transform_step(
        ...     xray, "Normalize Data",
        ...     items,
        ...     transform_fn=lambda item: {**item, "normalized": item['value'] / 100},
        ...     reason_fn=lambda orig, trans: f"Normalized {orig['value']} to {trans['normalized']}"
        ... )
    """
    transformed = []
    
    with step(xray, name, step_type="transform", input_data=input_data) as step_ctx:
        for item in items:
            entity_id = item.get(entity_id_key, str(item))
            transformed_item = transform_fn(item)
            transformed.append(transformed_item)
            
            if reason_fn:
                reason = reason_fn(item, transformed_item)
            else:
                reason = f"Transformed item {entity_id}"
            
            step_ctx.log_evaluation(
                entity_id=entity_id,
                value=transformed_item,
                passed=True,
                reason=reason
            )
        
        step_ctx.set_output({
            "transformed_count": len(transformed)
        })
    
    return transformed


def select_step(
    xray: XRay,
    name: str,
    items: List[Dict[str, Any]],
    select_fn: Optional[Callable[[List[Dict[str, Any]]], Dict[str, Any]]] = None,
    entity_id_key: str = "id",
    reason_fn: Optional[Callable[[Dict[str, Any]], str]] = None,
    input_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for selection steps.
    
    Automatically creates a selection step and returns the selected item.
    
    Args:
        xray: XRay instance
        name: Step name
        items: List of items to select from
        select_fn: Function that takes list of items and returns selected item (default: first item)
        entity_id_key: Key to use for entity_id (default: "id")
        reason_fn: Optional function to generate reason string (selected_item) -> str
        input_data: Additional input data for the step
    
    Returns:
        Selected item
    
    Example:
        >>> selected = select_step(
        ...     xray, "Select Best",
        ...     ranked_items,
        ...     select_fn=lambda items: max(items, key=lambda x: x['score']),
        ...     reason_fn=lambda item: f"Selected {item['name']} with highest score {item['score']}"
        ... )
    """
    if select_fn:
        selected = select_fn(items)
    else:
        selected = items[0] if items else None
    
    if not selected:
        raise ValueError("No items to select from")
    
    with step(xray, name, step_type="select", input_data=input_data) as step_ctx:
        entity_id = selected.get(entity_id_key, str(selected))
        
        if reason_fn:
            reason = reason_fn(selected)
        else:
            reason = f"Selected item {entity_id}"
        
        step_ctx.log_evaluation(
            entity_id=entity_id,
            value=selected,
            passed=True,
            reason=reason
        )
        
        step_ctx.set_output({
            "selected_id": entity_id,
            "selected_item": selected,
            "total_candidates": len(items)
        })
    
    return selected

