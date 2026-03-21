# yaya/ — Pakiet Python (top-level)

Pakiet top-level projektu — rezerwacja dla przyszłej modularyzacji.

---

## Struktura

```
yaya/
└── __init__.py   # Pusty plik init
```

---

## Opis

Pakiet `yaya` jest obecnie pusty. Zdefiniowany w `pyproject.toml` jako nazwa projektu (`name = "yaya"`).

Potencjalne zastosowania w przyszłości:
- Przeniesienie modułów z katalogu głównego do struktury pakietowej `yaya.*`
- Punkt wejścia `yaya.__main__` jako alternatywa dla `yolo-annotate.py`
- Reeksport API publicznego

Obecnie cały kod jest w katalogach: `engine/`, `Detectors/`, `Gui/`, `helpers/`, `views/`, `models/`, `Decorators/` oraz w plikach korzeniowych.
