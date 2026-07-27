# AI Log Analyzer

Proste MVP w terminalu, które analizuje jeden plik `.log`, tworzy lokalny raport Markdown i opcjonalnie prosi OpenAI o krótkie podsumowanie zagregowanych statystyk.

## Funkcje

- Rozpoznaje samodzielne tokeny `INFO`, `WARNING` i `ERROR`
- Liczy wpisy według poziomu
- Grupuje identyczne komunikaty `ERROR` i zlicza powtórzenia
- Zawsze tworzy lokalny raport Markdown bez AI
- Opcjonalny tryb `--ai` z najwyżej jednym wywołaniem OpenAI API
- Wysyła do modelu tylko zagregowane statystyki i maksymalnie 5 przykładowych błędów
- Zapisuje raport lokalny także wtedy, gdy brakuje klucza API albo żądanie się nie powiedzie

## Struktura projektu

```text
app.py                 punkt wejścia CLI
log_parser.py          lokalny parser i generator raportu
ai_summary.py          opcjonalne podsumowanie OpenAI
tests/                 testy lokalnego parsera
sample_logs/           przykładowy plik .log
pytest.ini             konfiguracja ścieżki dla pytest
requirements.txt       bezpośrednie zależności
.env.example           bezpieczny szablon zmiennych środowiskowych
report.md              wygenerowany wynik (ignorowany przez Git)
```

## Wymagania

- Zalecany Python 3.10+
- Bezpośrednie pakiety: `openai`, `python-dotenv`, `pytest`

## Instalacja w Windows PowerShell

```powershell
git clone https://github.com/OlafBrynda/ai-log-analyzer.git
cd ai-log-analyzer
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Jeśli Python Launcher jest niedostępny, zamiast `py` użyj `python`.

## Uruchamianie lokalne

```powershell
python app.py sample_logs\example.log
python app.py sample_logs\example.log --output my_report.md
```

Domyślny plik wynikowy: `report.md`.

## Argumenty CLI

| Argument | Opis |
| --- | --- |
| `log_path` | Wymagana ścieżka do jednego pliku `.log` |
| `--ai` | Prosi o jedno opcjonalne podsumowanie OpenAI |
| `--output PATH` | Zmienia ścieżkę pliku wynikowego (domyślnie: `report.md`) |

## Opcjonalne użycie AI

```powershell
python app.py sample_logs\example.log --ai
```

AI jest opcjonalne. Aplikacja działa bez klucza API i nadal zapisuje raport lokalny.

Jeśli brakuje klucza API albo żądanie OpenAI się nie powiedzie, raport lokalny i tak zostaje zapisany. Sekcja AI może wtedy zawierać:

```text
Podsumowanie AI jest niedostępne. Raport lokalny został wygenerowany prawidłowo.
```

### Konfiguracja `.env`

Skopiuj plik przykładowy i wpisz klucz API wyłącznie do lokalnego pliku `.env`. Nigdy nie commituj `.env`.

```powershell
Copy-Item .env.example .env
```

Przykładowe wartości:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-nano
```

## Testy

```powershell
python -m pytest
```

Testy obejmują wyłącznie lokalny parser. Nie wywołują OpenAI API.

## Przykładowy raport

Krótki przykład na podstawie `sample_logs/example.log`:

```markdown
# Raport AI Log Analyzer

**Analizowany plik:** `sample_logs/example.log`

## Podsumowanie lokalne

Rozpoznano 11 wpisów logu: 5 INFO, 2 WARNING i 4 ERROR.
Najczęściej powtarzający się błąd wystąpił 3 razy:
Connection refused by database host.

## Liczba wpisów według poziomu

| Poziom | Liczba |
| --- | ---: |
| INFO | 5 |
| WARNING | 2 |
| ERROR | 4 |

## Powtarzające się błędy

| Liczba | Komunikat |
| ---: | --- |
| 3 | Connection refused by database host |

## Podsumowanie AI

Podsumowanie AI nie zostało uruchomione dla tego wykonania.
```

## Prywatność i koszty

- Cały plik logu nigdy nie jest wysyłany do modelu
- Do żądania AI trafiają tylko zagregowane liczby i maksymalnie 5 unikalnych przykładowych komunikatów `ERROR`
- Przyczyny generowane przez AI są hipotezami, a nie potwierdzoną diagnozą
- Jedno uruchomienie z `--ai` wykonuje najwyżej jedno wywołanie `responses.create`

## Ograniczenia MVP

- Obsługuje tylko prosty podzbiór formatów logów
- Poziomy muszą występować jako samodzielne tokeny `INFO`, `WARNING` lub `ERROR`
- Grupowanie błędów opiera się na dokładnej równości oczyszczonego komunikatu
- W tym MVP nie ma interfejsu webowego, bazy danych, Dockera, RAG, agentów ani CI/CD
