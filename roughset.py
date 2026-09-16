"""
Rough Sets Mathematical Engine
Implements fundamental Rough Set Theory calculations:
- Indiscernibility classes (IND)
- Lower approximations and Positive Region (POS)
- Degree of dependency / Classification power (gamma)
- Attribute dispensability & indispensability
- Exhaustive minimal REDUCT discovery
- CORE computation (intersection of all reducts / indispensable attributes)
"""

from itertools import combinations
from typing import Any, Dict, List, Set, Tuple


def indiscernibility_classes(data: List[Dict[str, Any]], attributes: List[str]) -> List[List[int]]:
    """
    Computes equivalence classes of universe U for the given attribute subset.
    Returns a list of lists, where each sublist contains indices of objects that have
    identical values for all attributes in the specified list.
    """
    if not attributes:
        # If no attributes are selected, all objects are indiscernible from one another
        return [list(range(len(data)))]
    
    classes_map: Dict[Tuple[Any, ...], List[int]] = {}
    for idx, obj in enumerate(data):
        # Create a signature tuple of attribute values for the object
        sig = tuple(obj.get(attr) for attr in attributes)
        if sig not in classes_map:
            classes_map[sig] = []
        classes_map[sig].append(idx)
        
    return list(classes_map.values())


def positive_region(
    data: List[Dict[str, Any]],
    attributes: List[str],
    decision_attribute: str
) -> Set[int]:
    """
    Computes the decision-relative Positive Region POS_B(D).
    An equivalence class is included in the positive region if and only if
    all objects in that class have the exact same decision attribute value.
    Returns the set of object indices belonging to POS_B(D).
    """
    eq_classes = indiscernibility_classes(data, attributes)
    pos_region: Set[int] = set()
    
    for eq_class in eq_classes:
        # Determine all unique decision values in this equivalence class
        decision_values = {data[i].get(decision_attribute) for i in eq_class}
        # If the class is deterministic (consistent under decision D)
        if len(decision_values) == 1:
            pos_region.update(eq_class)
            
    return pos_region


def dependency_degree(
    data: List[Dict[str, Any]],
    attributes: List[str],
    decision_attribute: str
) -> float:
    """
    Calculates the degree of dependency (gamma_B(D)), also called Classification Power:
    gamma_B(D) = |POS_B(D)| / |U|
    Returns a float between 0.0 and 1.0.
    """
    if not data:
        return 0.0
    pos = positive_region(data, attributes, decision_attribute)
    return round(len(pos) / len(data), 4)


def is_dispensable(
    data: List[Dict[str, Any]],
    current_attributes: List[str],
    attribute_to_remove: str,
    decision_attribute: str
) -> bool:
    """
    Checks if attribute_to_remove is dispensable in current_attributes relative to decision_attribute.
    An attribute is dispensable if removing it maintains the original classification power:
    gamma_(B - {a})(D) == gamma_B(D)
    """
    if attribute_to_remove not in current_attributes:
        return False
    
    base_gamma = dependency_degree(data, current_attributes, decision_attribute)
    reduced_attrs = [a for a in current_attributes if a != attribute_to_remove]
    reduced_gamma = dependency_degree(data, reduced_attrs, decision_attribute)
    
    return reduced_gamma >= base_gamma


def is_indispensable(
    data: List[Dict[str, Any]],
    current_attributes: List[str],
    attribute: str,
    decision_attribute: str
) -> bool:
    """
    An attribute is indispensable if removing it strictly decreases classification power:
    gamma_(B - {a})(D) < gamma_B(D)
    """
    return not is_dispensable(data, current_attributes, attribute, decision_attribute)


def find_reducts(
    data: List[Dict[str, Any]],
    full_attributes: List[str],
    decision_attribute: str
) -> List[List[str]]:
    """
    Finds ALL decision-relative minimal REDUCTS of full_attributes with respect to decision_attribute.
    A subset R is a reduct if:
    1. gamma_R(D) == gamma_C(D)
    2. For every attribute r in R: gamma_(R - {r})(D) < gamma_C(D)  (minimality)
    """
    target_gamma = dependency_degree(data, full_attributes, decision_attribute)
    reducts: List[List[str]] = []
    
    # Check subsets by increasing size (1 to len(full_attributes))
    for k in range(1, len(full_attributes) + 1):
        for candidate_tuple in combinations(full_attributes, k):
            candidate = list(candidate_tuple)
            cand_gamma = dependency_degree(data, candidate, decision_attribute)
            
            # Condition 1: Same classification power
            if cand_gamma == target_gamma:
                # Condition 2: Minimality (no proper subset can achieve target_gamma)
                is_minimal = True
                for attr in candidate:
                    sub = [a for a in candidate if a != attr]
                    if dependency_degree(data, sub, decision_attribute) == target_gamma:
                        is_minimal = False
                        break
                
                if is_minimal:
                    reducts.append(candidate)
                    
    return reducts


def find_core(
    data: List[Dict[str, Any]],
    full_attributes: List[str],
    decision_attribute: str
) -> List[str]:
    """
    Calculates the decision-relative CORE.
    In Rough Sets, CORE(C, D) is the intersection of all reducts of C with respect to D,
    which is identically the set of indispensable attributes in C with respect to D.
    """
    reducts = find_reducts(data, full_attributes, decision_attribute)
    if not reducts:
        # If no reduct found (e.g. empty), check directly by indispensability
        return [
            attr for attr in full_attributes
            if is_indispensable(data, full_attributes, attr, decision_attribute)
        ]
    
    # Intersection of all reducts
    core_set = set(reducts[0])
    for r in reducts[1:]:
        core_set.intersection_update(r)
        
    return [attr for attr in full_attributes if attr in core_set]


def evaluate_candidate_reduct(
    data: List[Dict[str, Any]],
    candidate_attributes: List[str],
    full_attributes: List[str],
    decision_attribute: str
) -> Tuple[bool, str, float, float]:
    """
    Evaluates a candidate attribute subset chosen by the student.
    Returns (is_valid_minimal_reduct, status_code, candidate_gamma, target_gamma).
    
    Status codes:
    - 'valid_reduct': subset preserves target classification power AND is minimal.
    - 'classification_lost': subset has lower classification power than target.
    - 'not_minimal': subset preserves power, but contains superfluous/dispensable attributes.
    """
    target_gamma = dependency_degree(data, full_attributes, decision_attribute)
    candidate_gamma = dependency_degree(data, candidate_attributes, decision_attribute)
    
    if candidate_gamma < target_gamma:
        return False, "classification_lost", candidate_gamma, target_gamma
    
    # Check minimality
    for attr in candidate_attributes:
        reduced = [a for a in candidate_attributes if a != attr]
        if dependency_degree(data, reduced, decision_attribute) >= target_gamma:
            return False, "not_minimal", candidate_gamma, target_gamma
            
    return True, "valid_reduct", candidate_gamma, target_gamma
