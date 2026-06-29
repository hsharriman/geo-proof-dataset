from __future__ import annotations
from dataclasses import dataclass
from generate_wrong_proof.src.parsing.proof_parser import Step


@dataclass
class MutationContext:
    steps: list[Step]
    points: list[str]
    segments: list[str]
