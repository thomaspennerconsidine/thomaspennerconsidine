#!/usr/bin/env python3
"""Deterministic GitHub profile README generator and validator (stdlib only).

Usage:
    python3 scripts/profile.py check
    python3 scripts/profile.py render
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "config" / "profile.json"
README_PATH = ROOT / "README.md"
HEADER = "<!-- Generated from config/profile.json; edit that file, then run: python3 scripts/profile.py render -->"
TOP_LEVEL = {"$schema", "schema_version", "name", "tagline", "introduction", "specializations", "collaboration", "philosophy"}


class ProfileError(ValueError):
    """Raised for malformed profile configuration."""


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ProfileError(f"{path}: expected non-empty, trimmed text")
    if "\n" in value or "\r" in value or any(ord(char) < 32 for char in value):
        raise ProfileError(f"{path}: line breaks and control characters are not supported")
    return value


def _text_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ProfileError(f"{path}: expected a non-empty list")
    return [_text(item, f"{path}[{index}]") for index, item in enumerate(value)]


def validate(data: Any) -> dict[str, Any]:
    """Enforce the profile's documented structure without external packages."""
    if not isinstance(data, dict):
        raise ProfileError("Profile must be a JSON object")
    if set(data) != TOP_LEVEL:
        raise ProfileError(f"Profile keys mismatch. Missing: {sorted(TOP_LEVEL - set(data))}; unknown: {sorted(set(data) - TOP_LEVEL)}")
    if data["$schema"] != "./profile.schema.json":
        raise ProfileError("$schema must point to ./profile.schema.json")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ProfileError("Unsupported schema_version; expected integer 1")
    _text(data["name"], "name")
    _text(data["tagline"], "tagline")
    for field in ("introduction", "collaboration", "philosophy"):
        _text_list(data[field], field)
    entries = data["specializations"]
    if not isinstance(entries, list) or not entries:
        raise ProfileError("specializations: expected a non-empty list")
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        path = f"specializations[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"name", "description"}:
            raise ProfileError(f"{path}: expected only 'name' and 'description'")
        name = _text(entry["name"], f"{path}.name")
        _text(entry["description"], f"{path}.description")
        if name.casefold() in seen:
            raise ProfileError(f"{path}: duplicate specialization {name!r}")
        seen.add(name.casefold())
    return data


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    try:
        return validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileError(f"Could not read {path}: {exc}") from exc


def render(data: dict[str, Any]) -> str:
    validate(data)
    lines = [HEADER, "", f"# {data['name']}", "", f"**{data['tagline']}**", ""]
    for item in data["introduction"]:
        lines += [item, ""]
    lines += ["## 🔧 Technical Specializations", ""]
    for item in data["specializations"]:
        lines += [f"- **{item['name']}:** {item['description']}"]
    lines += ["", "## 💼 Consulting & Collaboration", "", "Interested in technical consulting, architecture development, and engineering collaborations involving:", ""]
    for item in data["collaboration"]:
        lines += [f"- {item}"]
    lines += ["", "## ⚙️ Engineering Philosophy", ""]
    for item in data["philosophy"]:
        lines += [item, ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "render"))
    args = parser.parse_args(argv)
    try:
        expected = render(load_profile())
        if args.command == "render":
            README_PATH.write_text(expected, encoding="utf-8", newline="\n")
            print(f"Rendered {README_PATH.relative_to(ROOT)}")
            return 0
        actual = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
        if actual != expected:
            print("README.md differs from config/profile.json. Run: python3 scripts/profile.py render", file=sys.stderr)
            sys.stderr.writelines(difflib.unified_diff(actual.splitlines(keepends=True), expected.splitlines(keepends=True), fromfile="README.md", tofile="expected"))
            return 1
        print("Profile config valid; README.md is synchronized")
        return 0
    except (ProfileError, OSError, UnicodeError) as exc:
        print(f"Profile validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
