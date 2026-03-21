# Gui/ — Warstwa prezentacji (widgety, rysowanie, kolory)

Narzędzia graficzne dla interfejsu PyQt5 — kolory, rysowanie OpenCV, niestandardowe widgety tabelowe. Moduły z tego pakietu są niezależne od logiki biznesowej i mogą być reużywane w dowolnym kontekście Qt.

---

## Struktura

```
Gui/
├── __init__.py
├── colors.py                              # Stałe kolorów BGR + schematy
├── drawing.py                             # Rysowanie detekcji na obrazach (OpenCV)
├── img/                                   # Zasoby graficzne
└── widgets/                               # Niestandardowe QTableWidgetItem
    ├── AnnotationsTableWidgetItem.py
    ├── BoolTableWidgetItem.py
    ├── EvalTableWidgetItem.py
    ├── FloatTableWidgetItem.py
    ├── HsvTableWidgetItem.py
    ├── ImageTableWidgetItem.py
    ├── ImhashTableWidgetItem.py
    ├── PercentTableWidgetItem.py
    ├── RectTableWidgetItem.py
    └── StatTableWidgetItem.py
```

---

## Moduły

### `colors.py` (153 linie)

Stałe kolorów w formacie **BGR** (konwencja OpenCV):

- Podstawowe: `white`, `black`, `red`, `green`, `blue`, `yellow`, `orange`, `cyan`, `pink`, ...
- Schematy: `colorSchemeBright` (13 żywych kolorów), `colorSchemeMatplotlib` (domyślna paleta matplotlib)
- Klasa `ColorCycler` — cykliczny iterator kolorów z wybranego schematu

**Uwaga:** duplikuje funkcjonalność `helpers/colors.py`. Istnieją dwie kopie ze względu na różne zależności importów w projekcie.

---

### `drawing.py`

Funkcje rysowania na obrazach OpenCV (`cv2`):

| Funkcja | Opis |
|---|---|
| `DrawDetections(image, detections, colors)` | Rysuje bounding-boxy detekcji z etykietami i confidence na obrazie |
| `DrawText(image, text, pos, ...)` | Rysuje tekst z opcjonalnym kolorowym tłem |
| `CreateColors(names)` | Generuje słownik `{nazwa: losowy_kolor_BGR}` dla klas |

---

## Podkatalog `widgets/` — Niestandardowe widgety tabelowe

Specjalizowane klasy `QTableWidgetItem` używane w tabelach widoków (`views/`). Wszystkie obsługują poprawne sortowanie numeryczne/chronologiczne (nie leksykograficzne jak domyślny `QTableWidgetItem`).

### `ImageTableWidgetItem` (120 linii)

Miniaturka obrazu w komórce tabeli:

- Opcjonalne przycinanie (crop) do regionu adnotacji
- Tooltip HTML z podglądem obrazka
- Cache miniaturek (deque, max 100 elementów)
- Konfigurowalne: rozmiar czcionki, kolor, podkreślenie

### `AnnotationsTableWidgetItem`

Podsumowanie adnotacji w komórce:

- Wyświetla listę klas z liczbą wystąpień: `"3 x C0\n1 x C2"`
- Filtrowanie po typie autora (`AnnoteAuthorType`)
- Sortowanie po hashu adnotacji

### `BoolTableWidgetItem`

Wartość bool z wizualnym feedbackiem:

- `True` → zielone tło, tekst "Yes"
- `False` → czerwone tło, tekst "No"
- Opcjonalne wymuszenie koloru tła

### `EvalTableWidgetItem`

Wynik ewaluacji adnotacji z kolorami:

| Ewaluacja | Kolor tła |
|---|---|
| `TruePositiveLabel` | Zielony |
| `TruePositive` | Jasnozielony |
| `FalseNegative` | Czerwony |
| `noEvaluation` | Niebieski |

### `FloatTableWidgetItem`

Liczba zmiennoprzecinkowa z:

- Konfigurowalna precyzja (domyślnie 2 miejsca)
- Poprawne sortowanie numeryczne (`__lt__`)

### `HsvTableWidgetItem`

Wartość HSV z kolorowym tłem:

- Kolor tła obliczany z `QColor.fromHsv()`
- Tekst czarny/biały automatycznie dobierany wg jasności
- Trzy tryby: hue, saturation, brightness (= value)

### `ImhashTableWidgetItem`

Perceptualny hash obrazu (image similarity):

- Duplikaty: czerwone tło z prefiksem „[D]"
- Unikaty: tło HSV wg wartości similarity
- Sortowanie po wartości hashu

### `PercentTableWidgetItem`

Wartość procentowa 0–100%:

- Opcjonalne kolorowanie tła (skala R→Y→G)
- Sortowanie numeryczne
- Wyświetlanie jako `"85.2%"`

### `RectTableWidgetItem`

Wymiary prostokąta `"W x H"`:

- Sortowanie po polu powierzchni (width × height)

### `StatTableWidgetItem`

Timestamp pliku (`os.stat`):

- Format: `"YYYY-MM-DD HH:MM:SS"`
- Sortowanie chronologiczne
