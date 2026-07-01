from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re


STEP_RE = re.compile(
    r"^\[(?P<num>\d+)\]\s*"
    r"(?P<reason>[A-Za-z_][A-Za-z0-9_]*)"
    r"\((?P<refs>[^)]*)\)\s*->\s*"
    r"(?P<statement>.+?)\s*$"
)


@dataclass
class Step:
    line_index: int
    raw: str
    num: int
    reason: str
    refs: str
    statement: str

    def render(self) -> str:
        return f"[{self.num:02d}] {self.reason}({self.refs}) -> {self.statement}"


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_steps(lines: list[str]) -> list[Step]:
    steps: list[Step] = []
    for i, line in enumerate(lines):
        m = STEP_RE.match(line.strip())
        if not m:
            continue
        steps.append(
            Step(
                line_index=i,
                raw=line.strip(),
                num=int(m.group("num")),
                reason=m.group("reason"),
                refs=m.group("refs"),
                statement=m.group("statement").strip(),
            )
        )
    return steps


def extract_points(lines: list[str]) -> list[str]:
    """
    Extract point names from a line like:
    pt: A (0, 0, t), B (0, 0, t), C (0, 0, t)
    """
    points: list[str] = []
    for line in lines:
        if not line.strip().startswith("pt:"):
            continue
        matches = re.findall(r"\b([A-Z][A-Za-z0-9]*)\s*\(", line)
        for p in matches:
            if p not in points:
                points.append(p)
    return points


def extract_segments(lines: list[str]) -> list[str]:
    """
    Extract segments from:
    seg: AB BC CD
    """
    segments: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("seg:"):
            continue
        rest = stripped[len("seg:"):].strip()
        for token in rest.split():
            if token.isalpha() and token.isupper() and len(token) == 2:
                if token not in segments:
                    segments.append(token)
    return segments


def split_args(arg_string: str) -> list[str]:
    """
    Split arguments inside a statement.

    Example:
    con_ang(a_LMN,a_RST) -> ["a_LMN", "a_RST"]
    """
    args = []
    current = []
    depth = 0
    for ch in arg_string:
        if ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        current.append(ch)
    if current:
        args.append("".join(current).strip())
    return args


def parse_statement(statement: str) -> tuple[str, list[str]] | None:
    """
    Example:
    con_ang(a_LMN,a_RST) -> ("con_ang", ["a_LMN", "a_RST"])
    """
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$", statement.strip())
    if not m:
        return None
    pred = m.group(1)
    args = split_args(m.group(2))
    return pred, args


def render_statement(pred: str, args: list[str]) -> str:
    return f"{pred}({','.join(args)})"