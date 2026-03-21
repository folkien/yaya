# Decorators/ — Dekoratory analizy datasetu

Moduły generujące raporty i wizualizacje na podstawie datasetu adnotacji. Wyspecjalizowane narzędzia do analizy rozkładu klas i jakości danych.

---

## Struktura

```
Decorators/
├── __init__.py
└── DecoratorDistributionShowcase.py   # Raport dystrybucji klas
```

---

## Moduły

### `DecoratorDistributionShowcase.py` (200 linii)

Klasa `DecoratorDistributionShowcase` — generator showcase'u rozkładu kategorii w datasecie.

**Cel:** wizualizacja jak wyglądają obiekty każdej klasy w datasecie. Tworzy raport Markdown z mozaikami obrazków per kategoria.

**Przepływ:**

1. `GetCategoriesAnnotations(df)` — dla każdej kategorii z DataFrame wybiera do 9 reprezentatywnych adnotacji (filtruje po medianie rozmiaru)
2. `GetCategoriesSubimages(categoriesAnnotations)` — wycina fragmenty obrazów (crop bounding-boxów) i zapisuje jako pliki PNG
3. Tworzy raport Markdown (`MarkdownReport`) z:
   - Nagłówkiem z wersją Git
   - Sekcjami per kategoria z miniaturkami
   - Statystykami rozkładu

**Konfiguracja:**
- `subdirectory` — podkatalog wyjściowy
- `categoryItems = 9` — max próbek na kategorię

**Zależności:** cv2, pandas, `helpers.textAnnotations`, `helpers.boxes`, `helpers.MarkdownReport`, `helpers.files`
