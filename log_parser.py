"""Lokalny, deterministyczny parser logów oraz generator raportu Markdown."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

LEVEL_PATTERN = re.compile(r"\b(INFO|WARNING|ERROR)\b")
MESSAGE_PREFIX = re.compile(r"^[\s:\-\]]+")


def parse_line(line: str) -> tuple[str, str] | None:
    """Parsuje jedną linię logu do pary (poziom, komunikat) albo None, gdy nierozpoznana."""
    match = LEVEL_PATTERN.search(line)
    if match is None:
        return None

    level = match.group(1)
    message = line[match.end() :]
    message = MESSAGE_PREFIX.sub("", message).strip()
    if not message:
        return None

    return level, message


def analyze_log(path: Path) -> dict[str, object]:
    """Analizuje plik logu i zwraca liczby wpisów oraz pogrupowane komunikaty ERROR."""
    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    error_counter: Counter[str] = Counter()

    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            parsed = parse_line(raw_line.rstrip("\n\r"))
            if parsed is None:
                continue

            level, message = parsed
            counts[level] += 1
            if level == "ERROR":
                error_counter[message] += 1

    error_groups = sorted(
        error_counter.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return {
        "counts": counts,
        "error_groups": error_groups,
        "total_recognized": sum(counts.values()),
    }


def _local_summary(stats: dict[str, object]) -> str:
    """Buduje krótkie lokalne podsumowanie na podstawie zagregowanych statystyk."""
    counts = stats["counts"]
    total = stats["total_recognized"]
    error_groups = stats["error_groups"]

    if total == 0:
        return "W tym pliku nie znaleziono rozpoznanych wpisów logu."

    info = counts["INFO"]
    warning = counts["WARNING"]
    error = counts["ERROR"]
    summary = (
        f"Rozpoznano {total} wpisów logu: "
        f"{info} INFO, {warning} WARNING i {error} ERROR."
    )

    if error == 0:
        return summary + " Nie znaleziono wpisów ERROR."

    repeated = [group for group in error_groups if group[1] > 1]
    if not repeated:
        return summary + " Wystąpiły wpisy ERROR, ale żaden się nie powtórzył."

    top_message, top_count = repeated[0]
    return (
        summary
        + f" Najczęściej powtarzający się błąd wystąpił {top_count} razy: {top_message}."
    )


def _counts_table(counts: dict[str, int]) -> str:
    """Renderuje prostą tabelę Markdown z liczbą wpisów według poziomu."""
    lines = [
        "| Poziom | Liczba |",
        "| --- | ---: |",
        f"| INFO | {counts['INFO']} |",
        f"| WARNING | {counts['WARNING']} |",
        f"| ERROR | {counts['ERROR']} |",
    ]
    return "\n".join(lines)


def _repeated_errors_section(error_groups: list[tuple[str, int]]) -> str:
    """Renderuje sekcję powtarzających się błędów."""
    repeated = [group for group in error_groups if group[1] > 1]
    if not error_groups:
        return "Nie znaleziono wpisów ERROR."
    if not repeated:
        return "Nie znaleziono powtarzających się komunikatów ERROR."

    lines = ["| Liczba | Komunikat |", "| ---: | --- |"]
    for message, count in repeated:
        safe_message = message.replace("|", "\\|")
        lines.append(f"| {count} | {safe_message} |")
    return "\n".join(lines)


def build_report(
    stats: dict[str, object],
    source: Path,
    ai_section: str | None,
) -> str:
    """Buduje pełny raport Markdown ze statystyk lokalnych i opcjonalnej sekcji AI."""
    counts = stats["counts"]
    error_groups = stats["error_groups"]

    if ai_section is None:
        ai_text = "Podsumowanie AI nie zostało uruchomione dla tego wykonania."
    else:
        ai_text = ai_section

    sections = [
        "# Raport AI Log Analyzer",
        "",
        f"**Analizowany plik:** `{source.as_posix()}`",
        "",
        "## Podsumowanie lokalne",
        "",
        _local_summary(stats),
        "",
        "## Liczba wpisów według poziomu",
        "",
        _counts_table(counts),
        "",
        "## Powtarzające się błędy",
        "",
        _repeated_errors_section(error_groups),
        "",
        "## Podsumowanie AI",
        "",
        ai_text,
        "",
    ]
    return "\n".join(sections)
