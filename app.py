"""Punkt wejścia CLI dla AI Log Analyzer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from log_parser import analyze_log, build_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parsuje argumenty wiersza poleceń."""
    parser = argparse.ArgumentParser(
        description="Analizuje plik .log i zapisuje raport Markdown.",
    )
    parser.add_argument(
        "log_path",
        type=Path,
        help="Ścieżka do jednego pliku .log",
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Opcjonalnie zleca jedno podsumowanie OpenAI na podstawie zagregowanych statystyk",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("report.md"),
        help="Ścieżka pliku Markdown wynikowego (domyślnie: report.md)",
    )
    return parser.parse_args(argv)


def validate_log_path(path: Path) -> str | None:
    """Zwraca komunikat błędu, gdy ścieżka jest nieprawidłowa, w przeciwnym razie None."""
    if not path.exists():
        return f"Błąd: nie znaleziono pliku: {path}"
    if not path.is_file():
        return f"Błąd: podana ścieżka nie prowadzi do pliku: {path}"
    if path.suffix.lower() != ".log":
        return f"Błąd: oczekiwano pliku z rozszerzeniem .log: {path}"
    return None


def main(argv: list[str] | None = None) -> int:
    """Uruchamia analizę i zapisuje raport Markdown."""
    args = parse_args(argv)
    log_path: Path = args.log_path

    error = validate_log_path(log_path)
    if error is not None:
        print(error, file=sys.stderr)
        return 1

    stats = analyze_log(log_path)

    ai_section: str | None = None
    if args.ai:
        from ai_summary import generate_ai_summary

        ai_section = generate_ai_summary(stats)

    report = build_report(stats, log_path, ai_section)
    output_path: Path = args.output
    output_path.write_text(report, encoding="utf-8")
    print(f"Raport zapisano do: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
