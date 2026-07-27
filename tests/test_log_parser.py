"""Testy lokalnego parsera logów."""

from pathlib import Path

from log_parser import analyze_log, parse_line


def test_counts_info_warning_error(tmp_path: Path) -> None:
    log_file = tmp_path / "levels.log"
    log_file.write_text(
        "\n".join(
            [
                "2024-01-01 INFO Service started",
                "2024-01-01 WARNING Disk space low",
                "2024-01-01 ERROR Connection refused",
                "2024-01-01 INFO Health check passed",
                "2024-01-01 WARNING Retry scheduled",
            ]
        ),
        encoding="utf-8",
    )

    stats = analyze_log(log_file)

    assert stats["counts"] == {"INFO": 2, "WARNING": 2, "ERROR": 1}
    assert stats["total_recognized"] == 5


def test_groups_identical_errors(tmp_path: Path) -> None:
    log_file = tmp_path / "errors.log"
    log_file.write_text(
        "\n".join(
            [
                "ERROR Connection refused",
                "ERROR Timeout waiting for response",
                "ERROR Connection refused",
            ]
        ),
        encoding="utf-8",
    )

    stats = analyze_log(log_file)

    assert stats["counts"]["ERROR"] == 3
    assert stats["error_groups"] == [
        ("Connection refused", 2),
        ("Timeout waiting for response", 1),
    ]


def test_ignores_invalid_and_empty_lines() -> None:
    assert parse_line("") is None
    assert parse_line("   ") is None
    assert parse_line("plain text without a level") is None
    assert parse_line("EROR mistyped level token") is None
    assert parse_line("INFORMATION is not a standalone level") is None
    assert parse_line("INFO") is None
    assert parse_line("WARNING:") is None
    assert parse_line("ERROR -") is None
    assert parse_line("[ERROR]") is None
