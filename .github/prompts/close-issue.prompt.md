---
agent: agent
description: "Zamknięcie issue - ekstrakcja wiedzy do wiedza/ i archiwizacja lub usunięcie katalogu"
---

# Procedura zamknięcia issue

Wykonaj poniższe kroki w podanej kolejności.

## Krok 1 – Identyfikacja

Użytkownik podał nazwę issue do zamknięcia. Otwórz docs/issues/{nazwa_pliku}
Zapoznaj się z  pełną treścią.

## Krok 2 – Analiza wiedzy

Oceń każdy plik/element katalogu według poniższego klucza:

| Typ wiedzy | Gdzie zapisać |
|---|---|
| Specyfikacja techniczna / dokumentacja | `docs/` lub adekwatny podkatalog |
| Dookumentacja użytkownika / zmiany w interfejsie | Zaktualizuj tylko wersję angielską `wiki/en/`  |


Przejrzyj `README.md` w głównym katalogu repozytorium i jeżeli jest coś ważnego lub wymaganego zaktualizuj je.


## Krok 5 – Zapytaj o los katalogu

Użyj narzędzia `vscode_askQuestions` (NIE pytaj tekstowo) z pytaniem:

```
question: "Czy usunąć plik issue_{nazwa}?"
header: "usunmiecie"
options:
  - label: "usuń – trwale usuń katalog (rm -rf)"
  - label: "archiwum – przenieś do docs/issues_resoled/issue_{nazwa}"
```

## Krok 6 – Wykonaj akcję

Na podstawie odpowiedzi użytkownika wykonaj:

**Usunięcie:**
```bash
rm -rf issue_{nazwa}/
```

**Przeniesienie do archiwum:**
```bash
mv issue_{nazwa}/ docs/issues_resoled/issue_{nazwa}/
```

Potwierdź wykonanie.
