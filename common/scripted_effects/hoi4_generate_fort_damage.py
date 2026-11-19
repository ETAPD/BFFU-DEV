#!/usr/bin/env python3
"""Generate a HOI4 scripted effect that damages forts in every province of a state.

The generated effect uses a state-ID check and explicit province IDs, avoiding
unsupported province-iteration effects. Supply state history directories in
load order: base game first, then mods that override/add states.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator

STATE_OPEN_RE = re.compile(r"\bstate\s*=\s*\{")
ID_RE = re.compile(r"\bid\s*=\s*(\d+)\b")
PROVINCES_OPEN_RE = re.compile(r"\bprovinces\s*=\s*\{")


def strip_comments(text: str) -> str:
    # HOI4 history files use # for line comments.
    return re.sub(r"(?m)#.*$", "", text)


def extract_braced_block(text: str, open_brace: int) -> tuple[str, int] | None:
    """Return text inside the brace at open_brace and the index after its close."""
    if open_brace >= len(text) or text[open_brace] != "{":
        return None
    depth = 0
    in_quote = False
    escaped = False
    for i in range(open_brace, len(text)):
        ch = text[i]
        if in_quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_quote = False
            continue
        if ch == '"':
            in_quote = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace + 1 : i], i + 1
    return None


def extract_states(file_path: Path) -> Iterator[tuple[int, list[int]]]:
    raw = file_path.read_text(encoding="utf-8-sig", errors="replace")
    text = strip_comments(raw)

    for match in STATE_OPEN_RE.finditer(text):
        open_brace = text.find("{", match.start(), match.end())
        state_block_result = extract_braced_block(text, open_brace)
        if state_block_result is None:
            continue
        state_block, _ = state_block_result

        id_match = ID_RE.search(state_block)
        if not id_match:
            continue
        state_id = int(id_match.group(1))

        provinces_match = PROVINCES_OPEN_RE.search(state_block)
        if not provinces_match:
            continue
        provinces_open = state_block.find("{", provinces_match.start(), provinces_match.end())
        provinces_result = extract_braced_block(state_block, provinces_open)
        if provinces_result is None:
            continue
        provinces_block, _ = provinces_result
        province_ids = sorted({int(value) for value in re.findall(r"\b\d+\b", provinces_block)})

        if province_ids:
            yield state_id, province_ids


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate repairable fort-damage effects for every province in any target state."
    )
    parser.add_argument(
        "--states-dir",
        action="append",
        required=True,
        type=Path,
        help="A history/states directory. Repeat for mods; later directories override earlier state IDs.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output .txt file inside your mod's common/scripted_effects folder.",
    )
    parser.add_argument("--fort-tag", default="fort", help="Building tag for land forts (default: fort).")
    parser.add_argument(
        "--coastal-fort-tag",
        default="coastal_fort",
        help="Building tag for coastal forts (default: coastal_fort).",
    )
    parser.add_argument("--damage", default="2", help="Damage amount for each building (default: 2).")
    args = parser.parse_args()

    # Keep state definitions from the last supplied directory when IDs repeat.
    states: dict[int, list[int]] = {}
    files_read = 0
    for root in args.states_dir:
        if not root.is_dir():
            print(f"ERROR: state history directory does not exist: {root}", file=sys.stderr)
            return 2
        for file_path in sorted(root.rglob("*.txt")):
            files_read += 1
            try:
                for state_id, province_ids in extract_states(file_path):
                    states[state_id] = province_ids
            except OSError as exc:
                print(f"WARNING: could not read {file_path}: {exc}", file=sys.stderr)

    if not states:
        print("ERROR: no state definitions with province lists were found.", file=sys.stderr)
        return 1

    lines: list[str] = [
        "# AUTO-GENERATED FILE. Regenerate after changing state province lists.",
        "# Call this scripted effect from inside var:target_state = { ... }.",
        "# It applies normal, repairable building damage to each listed province.",
        "",
        "raid_damage_all_provinces_in_target_state = {",
    ]

    for state_id in sorted(states):
        province_ids = states[state_id]
        lines.extend(
            [
                "\tif = {",
                f"\t\tlimit = {{ state = {state_id} }}",
            ]
        )
        for province_id in province_ids:
            lines.extend(
                [
                    "\t\tdamage_building = {",
                    f"\t\t\ttags = {args.fort_tag}",
                    f"\t\t\tdamage = {args.damage}",
                    f"\t\t\tprovince = {province_id}",
                    "\t\t}",
                    "\t\tdamage_building = {",
                    f"\t\t\ttags = {args.coastal_fort_tag}",
                    f"\t\t\tdamage = {args.damage}",
                    f"\t\t\tprovince = {province_id}",
                    "\t\t}",
                ]
            )
        lines.append("\t}")

    lines.append("}")
    lines.append("")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")

    province_count = sum(len(ids) for ids in states.values())
    print(f"Read {files_read} state-history files.")
    print(f"Generated {len(states)} state branches covering {province_count} province entries.")
    print(f"Output: {args.output}")
    print("Add the output file to common/scripted_effects in your mod, then call:")
    print("raid_damage_all_provinces_in_target_state = yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
