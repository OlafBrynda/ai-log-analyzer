"""Opcjonalne generowanie podsumowania OpenAI na podstawie zagregowanych statystyk logu."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

DEFAULT_MODEL = "gpt-5-nano"
UNAVAILABLE_MESSAGE = (
    "Podsumowanie AI jest niedostępne. Raport lokalny został wygenerowany prawidłowo."
)


def _build_prompt(stats: dict[str, object]) -> str:
    """Buduje zwięzły prompt wyłącznie z zagregowanych statystyk."""
    counts = stats["counts"]
    error_groups = stats["error_groups"]
    total = stats["total_recognized"]
    top_errors = error_groups[:5]
    sample_errors = [message for message, _ in error_groups[:5]]

    top_lines = (
        "\n".join(f"- ({count}) {message}" for message, count in top_errors)
        or "- brak"
    )
    sample_lines = (
        "\n".join(f"- {message}" for message in sample_errors) or "- brak"
    )

    return (
        "Pomagasz analizować logi aplikacji. "
        "Używaj wyłącznie zagregowanych statystyk podanych poniżej. "
        "Nie wymyślaj dokładnych linii logu, których nie przekazano. "
        "Odpowiedź napisz wyłącznie po polsku.\n\n"
        f"Liczba INFO: {counts['INFO']}\n"
        f"Liczba WARNING: {counts['WARNING']}\n"
        f"Liczba ERROR: {counts['ERROR']}\n"
        f"Łączna liczba rozpoznanych wpisów: {total}\n\n"
        "Najczęstsze komunikaty ERROR:\n"
        f"{top_lines}\n\n"
        "Do 5 unikalnych przykładowych komunikatów ERROR:\n"
        f"{sample_lines}\n\n"
        "Napisz krótką odpowiedź z dokładnie tymi trzema sekcjami:\n"
        "1. Najważniejsze problemy\n"
        "2. Możliwe przyczyny (hipotezy)\n"
        "3. Sugerowane następne kroki\n"
        "Każdą możliwą przyczynę rozpocznij od słowa „Hipoteza:” "
        "i nie przedstawiaj jej jako potwierdzonej diagnozy.\n"
    )


def generate_ai_summary(stats: dict[str, object]) -> str:
    """Generuje podsumowanie AI ze statystyk albo bezpieczny komunikat przy błędzie."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    if not api_key:
        return UNAVAILABLE_MESSAGE

    prompt = _build_prompt(stats)

    try:
        client = OpenAI()
        response = client.responses.create(
            model=model_name,
            input=prompt,
        )
        summary = response.output_text
    except OpenAIError:
        return UNAVAILABLE_MESSAGE

    if not summary or not str(summary).strip():
        return UNAVAILABLE_MESSAGE

    return str(summary).strip()
