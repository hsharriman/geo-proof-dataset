from __future__ import annotations


MUTATION_TYPES = {
    "permutation_non_tree": {
        "mutation_group": "non_control",
        "weight": 1,
    },
    "permutation_tree": {
        "mutation_group": "control",
        "weight": 1,
    },

    # later
    "mixed_up_theorems": {
        "mutation_group": "control",
        "weight": 2,
    },
    "remove_step": {
        "mutation_group": "control",
        "weight": 2,
    },
    "circular_reasoning": {
        "mutation_group": "control",
        "weight": 3,
    },
}


MUTATION_FIELDS = (
    "before",
    "after",
    "corruption_type",
    "mutation_type",
    "mutation_group",
    "classifier_label",
)


def known_mutation_types() -> set[str]:
    return set(MUTATION_TYPES)


def mutation_group(mutation_type: str) -> str:
    return MUTATION_TYPES[mutation_type]["mutation_group"]


def mutation_weight(mutation_type: str) -> int:
    return MUTATION_TYPES[mutation_type]["weight"]


def selected_mutation_types(values: list[str] | None, default_all: bool) -> set[str]:
    if not values:
        return known_mutation_types() if default_all else set()
    if "all" in values:
        return known_mutation_types()
    selected_types = set(values)
    unknown_types = selected_types - known_mutation_types()
    if unknown_types:
        raise ValueError(f"Unknown mutation type(s): {sorted(unknown_types)}")
    return selected_types


def validate_required_types(
    allowed_types: set[str],
    required_types: set[str],
    mutations_per_proof: int | None,
) -> None:
    if not required_types.issubset(allowed_types):
        raise ValueError("Required mutation types must be allowed.")

    if mutations_per_proof is not None and len(required_types) > mutations_per_proof:
        raise ValueError("Required mutation types cannot exceed --mutations-per-proof")


def mutation_types_in(mutations: list[dict]) -> set[str]:
    return {mutation["mutation_type"] for mutation in mutations}


def keep_mutation(mutation: dict, allowed_types: set[str]) -> bool:
    return mutation["mutation_type"] in allowed_types


def chain_has_required_types(mutations: list[dict], required_types: set[str]) -> bool:
    return required_types.issubset(mutation_types_in(mutations))


def forced_next_type(
    mutations: list[dict],
    required_types: set[str],
    mutations_per_proof: int,
) -> str | None:
    missing_types = sorted(required_types - mutation_types_in(mutations))
    remaining_slots = mutations_per_proof - len(mutations)
    if len(missing_types) >= remaining_slots:
        return missing_types[0]
    return None


def build_mutation(
    step,
    before: str,
    after: str,
    corruption_type: str,
    mutation_type: str,
    edit_distance: int = 1,
) -> dict | None:
    if before == after:
        return None
    group = mutation_group(mutation_type)
    return {
        "step": step,
        "before": before,
        "after": after,
        "corruption_type": corruption_type,
        "mutation_type": mutation_type,
        "mutation_group": group,
        "classifier_label": group,
        "edit_distance": edit_distance,
        "weight": mutation_weight(mutation_type),
    }


def mutation_key(mutation: dict) -> tuple[int, str, str]:
    step = mutation["step"]
    return step.num, mutation["before"], mutation["after"]


def chain_key(mutations: list[dict]) -> tuple[tuple[int, str, str], ...]:
    return tuple(mutation_key(mutation) for mutation in mutations)


def mutation_metadata(mutation: dict) -> dict:
    step = mutation["step"]
    metadata = {
        "step": step.num,
        "reason_kept": step.reason,
    }
    for field in MUTATION_FIELDS:
        metadata[field] = mutation[field]
    return metadata


def chain_metadata(source: str, output: str, wrong_id: str, mutations: list[dict]) -> dict:
    return {
        "source": source,
        "output": output,
        "wrong_id": wrong_id,
        "num_mutations": len(mutations),
        "mutation_types": sorted(mutation_types_in(mutations)),
        "mutation_groups": sorted({mutation["mutation_group"] for mutation in mutations}),
        "steps": [mutation["step"].num for mutation in mutations],
        "edit_distance": sum(mutation["edit_distance"] for mutation in mutations),
        "mutation_score": sum(mutation["weight"] * mutation["edit_distance"] for mutation in mutations),
        "mutations": [mutation_metadata(mutation) for mutation in mutations],
    }