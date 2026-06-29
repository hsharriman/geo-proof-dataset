from __future__ import annotations

from generate_wrong_proof.src.mutation.mutation_context import MutationContext
from generate_wrong_proof.src.parsing.proof_parser import Step


def remove_step_mutations(
    step: Step,
    context: MutationContext,
) -> list[dict]:
    return []
