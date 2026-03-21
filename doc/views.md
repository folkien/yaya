# views/ — Widoki tabel (generowanie zawartości QTableWidget)

Klasy statyczne generujące zawartość tabel w interfejsie GUI. Każdy widok przyjmuje `QTableWidget` i listę danych plików z `Annoter`, a następnie wypełnia tabelę odpowiednimi kolumnami i widgetami z `Gui/widgets/`.

---

## Struktura

```
views/
├── ViewAnnotations.py      # Tabela adnotacji (human)
├── ViewDetections.py        # Tabela detekcji (detector)
├── ViewFilters.py           # Grid przycisków filtrujących
├── ViewImagesSummary.py     # Podsumowanie metryczne
└── ViewImagesTable.py       # Główna tabela plików obrazów
```

---

## Moduły

### `ViewImagesTable.py` — Główna tabela plików (294 linie)

Klasa `ViewImagesTable` z metodami statycznymi `View()` i `ViewRow()`.

Wypełnia tabelę danymi o plikach obrazów — jedna linia per plik:

| Kolumna | Widget | Opis |
|---|---|---|
| Name | `ImageTableWidgetItem` | Miniaturka + nazwa pliku |
| ImSize | `RectTableWidgetItem` | Wymiary obrazu (W×H) |
| Annotated | `BoolTableWidgetItem` | Czy istnieje plik adnotacji |
| Validation | `BoolTableWidgetItem` | Czy jest w datasecie |
| Correct | `PercentTableWidgetItem` | % poprawności |
| Classes | `AnnotationsTableWidgetItem` | Lista klas adnotacji |
| Dets | `AnnotationsTableWidgetItem` | Lista klas detekcji |
| Time | `StatTableWidgetItem` | Data modyfikacji pliku |
| Hue, Sat, Bri | `HsvTableWidgetItem` | Wartości HSV obrazu |
| ImHash | `ImhashTableWidgetItem` | Perceptualny hash (duplikaty) |
| IOU | `FloatTableWidgetItem` | Średnie IOU |
| OverlapIOU | `FloatTableWidgetItem` | IOU nakładania |
| Size | `RectTableWidgetItem` | Średni rozmiar adnotacji |
| CorrectBbox | `PercentTableWidgetItem` | % poprawnych bboxów |
| Precision | `PercentTableWidgetItem` | Precision |
| Recall | `PercentTableWidgetItem` | Recall |
| Errors | `FloatTableWidgetItem` | Liczba błędów |
| Match.Confidence | `PercentTableWidgetItem` | Confidence dopasowań |
| Det.WorstConfidence | `PercentTableWidgetItem` | Najgorszy confidence detekcji |

Kolumny HSV mają stałą szerokość 50px. Po wypełnieniu włącza sortowanie i dopasowuje rozmiary kolumn.

---

### `ViewAnnotations.py` — Tabela adnotacji (176 linii)

Klasa `ViewAnnotations` z metodą statyczną `View()`.

Wyświetla **wszystkie adnotacje** (typ: human) ze wszystkich plików — jedna linia per adnotacja:

| Kolumna | Widget | Opis |
|---|---|---|
| File/ID | `ImageTableWidgetItem` | Miniaturka crop adnotacji + nazwa |
| Cat | `QTableWidgetItem` | Kategoria (nazwa klasy) |
| Conf | `PercentTableWidgetItem` | Confidence ewaluacji |
| Eval | `EvaluationTableWidgetItem` | TP/FN/brak |
| EvalClass | `QTableWidgetItem` | Nazwa klasy z ewaluacji |
| Size | `RectTableWidgetItem` | Rozmiar bboxa (piksele) |
| Ratio | `FloatTableWidgetItem` | Stosunek W/H |
| Area | `FloatTableWidgetItem` | Powierzchnia bboxa |
| Area/Image | `PercentTableWidgetItem` | % powierzchni obrazu |
| Hue, Saturation, Brightness | `HsvTableWidgetItem` | HSV wycinka adnotacji |

Obsługuje filtrowanie po klasach (`filter_classes`).

---

### `ViewDetections.py` — Tabela detekcji (199 linii)

Klasa `ViewDetections` z metodą statyczną `View()`.

Analogiczna do `ViewAnnotations`, ale dla **detekcji detektora** — jedna linia per detekcja:

| Kolumna | Widget | Opis |
|---|---|---|
| File/ID | `ImageTableWidgetItem` | Miniaturka crop detekcji |
| Cat | `QTableWidgetItem` | Kategoria |
| Conf | `PercentTableWidgetItem` | Confidence detektora |
| Eval | `EvaluationTableWidgetItem` | Wynik ewaluacji |
| Size | `RectTableWidgetItem` | Rozmiar bboxa |
| Ratio, Area, Area/Image | odpowiednie widgety | Proporcje i powierzchnia |
| Hue, Saturation, Brightness | `HsvTableWidgetItem` | HSV wycinka |

Różnice vs `ViewAnnotations`: źródło danych to `fileEntry["Detections"]` zamiast `fileEntry["Annotations"]`, dodatkowe pole `is_annotated`.

---

### `ViewFilters.py` — Grid przycisków filtrujących (140 linii)

Klasa `ViewFilters` z metodą statyczną `ViewClasses()`.

Dynamicznie tworzy grid `QPushButton` w `QGridLayout`:

- Przyciski checkable (wielokrotny wybór)
- `QButtonGroup` z `setExclusive(False)`
- Tooltip z pełną nazwą klasy
- Konfiguracja: max szerokość przycisku, elementy na wiersz, domyślny stan
- Callback wywoływany przy kliknięciu z ID przycisku

Statyczne handlery grup przycisków:
- `filter_images_group` — filtr typów obrazów
- `filter_classes_group` — filtr klas adnotacji
- `filter_detections_group` — filtr klas detekcji

---

### `ViewImagesSummary.py` — Podsumowanie metryczne (96 linii)

**Dataclass `Summary`** — agreguje metryki z wszystkich plików:

| Property | Opis |
|---|---|
| `correct` | Średni % poprawnych obrazów |
| `correct_bboxes` | Średni % poprawnych bboxów |
| `precision` | Średnia precision |
| `recall` | Średni recall |
| `new_detections` | Suma nowych detekcji |

Metoda `Add(fileEntry)` — dodaje dane z jednego pliku do sumy.

**Klasa `ViewImagesSummary`** z metodą statyczną `View(label, files)`:

- Oblicza `Summary` z listy plików
- Aktualizuje `QLabel` tekstem podsumowania (format tekstowy z metrykami %)
