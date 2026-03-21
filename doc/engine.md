# engine/ — Logika biznesowa (rdzeń aplikacji)

Centralny pakiet z logiką domenową aplikacji YAYA. Nie zależy od PyQt5 — zawiera wyłącznie logikę przetwarzania adnotacji, plików i konfiguracji.

---

## Struktura

```
engine/
├── __init__.py
├── annoter.py              # Główny silnik adnotacji
├── annote.py               # Model adnotacji bounding-box
├── annote_enums.py          # Enumy (autor, ewaluacja, typ annotatora)
├── config_toml.py           # Czytnik konfiguracji TOML (Singleton)
├── dataset.py               # Zarządzanie plikiem dataset.txt
├── GuiClassKeycodes.py      # Mapowanie klawiszy → numery klas
├── session.py               # Sesja — snapshot plików do temp/
└── annotators/              # Strategie wizualizacji adnotacji
    ├── annotator.py         # Dispatcher (fasada)
    ├── annotator_default.py
    ├── annotator_confidence_heat.py
    └── annotator_category.py
```

---

## Moduły

### `annoter.py` — klasa `Annoter` (840 linii)

Główny silnik adnotacji obrazów. Zarządza:

- **Listą plików** obrazów w katalogu (skanowanie, sortowanie, nawigacja next/prev)
- **Detekcjami** — integracja z detektorami YOLO (uruchamianie, cache wyników)
- **Adnotacjami** — ładowanie/zapisywanie `.txt`, porównywanie z detekcjami
- **Metrykami** — ewaluacja TP/FP/FN/Precision/Recall per plik
- **Wizualnymi** — cache HSV/hash per obraz (`.visuals.json`)
- **Filtrowaniem** — only new/old/error files, only specific class
- **Datasetem** — integracja z `dataset.txt`

Enum `DetectorSelected` (Default / YoloWorld) pozwala przełączać detektor w runtime.

**Kluczowe zależności:** `engine.annote`, `engine.dataset`, `Detectors.common.Detector`, `helpers.textAnnotations`, `helpers.metrics`, `helpers.visuals`

---

### `annote.py` — klasa `Annote` (316 linii)

Model pojedynczej adnotacji bounding-box. Przechowuje:

- `box` — współrzędne znormalizowane (xywh, 0–1)
- `classNumber` / `className` — klasa obiektu
- `confidence` — pewność detekcji (0–100)
- `authorType` — `AnnoteAuthorType` (człowiek / detektor / ręczny)
- `evalution` — wynik ewaluacji (`AnnoteEvaluation`)
- `hue`, `saturation`, `brightness` — wartości HSV wycinka obrazu

Funkcje modułowe:

| Funkcja | Opis |
|---|---|
| `Init(names)` | Inicjalizacja globalnej listy nazw klas |
| `GetClasses()` | Zwraca listę nazw klas |
| `GetClassName(number)` | Nazwa klasy po numerze |
| `GetClassNumber(name)` | Numer klasy po nazwie |
| `toTxtAnnote(annote)` | Konwersja do formatu pliku `.txt` |
| `fromTxtAnnote(txt)` | Tworzenie `Annote` z rekordu `.txt` |
| `toYoloDetection(annote)` | Konwersja do formatu detekcji YOLO |
| `fromDetection(detection)` | Tworzenie `Annote` z detekcji |

---

### `annote_enums.py`

Trzy enumeracje:

| Enum | Wartości | Opis |
|---|---|---|
| `AnnoteAuthorType` | byHuman, byDetector, byHand | Kto utworzył adnotację |
| `AnnoteEvaluation` | noEvaluation, TruePositiveLabel, TruePositive, FalseNegative | Wynik porównania z detekcją |
| `AnnotatorType` | Default, ConfidenceHeat, Category | Styl wizualizacji w edytorze |

---

### `dataset.py` — klasa `Dataset`

Zarządza plikiem `dataset.txt` — zbiorem ścieżek do plików w datasecie treningowym.

| Metoda | Opis |
|---|---|
| `add(path)` | Dodaje ścieżkę do zbioru |
| `remove(path)` | Usuwa ścieżkę ze zbioru |
| `load(path)` | Wczytuje plik, waliduje istnienie plików |
| `save()` | Zapisuje posortowane ścieżki do pliku |
| `is_inside(path)` | Sprawdza czy ścieżka jest w zbiorze |

Automatycznie usuwa wpisy wskazujące na nieistniejące pliki przy wczytywaniu.

---

### `session.py` — klasa `Session` (dataclass)

Przechowuje timestamp sesji i umożliwia tworzenie snapshot'ów plików:

- Kopiuje obraz + towarzyszące pliki (`.txt`, `.detector`, `.visuals`) do katalogu `temp/session_YYYYMMDD_HHMM/`
- Metoda `fileentry_store(fileEntry)` — kopiuje plik na podstawie słownika danych pliku

---

### `config_toml.py` — klasa `ConfigToml` (Singleton)

Czytnik konfiguracji TOML z fallbackiem:

1. Próbuje wczytać `config.toml`
2. Jeśli nie istnieje → `config.example.toml`
3. Jeśli żaden nie istnieje → `FileNotFoundError`

Metody `get(key, default)` i `__getitem__(key)`.

---

### `GuiClassKeycodes.py` — klasa `GuiClassKeycodes`

Mapowanie klawiszy klawiatury na numery klas adnotacji:

- Klawisze `1-9, 0, -, =` → klasy 0–11
- Klawisz `` ` `` (backtick) → przesunięcie offsetu o +12 (dla datasetów z >12 klasami)
- Cykliczne zawijanie offsetu po przekroczeniu maksymalnej liczby klas

---

## Podkatalog `annotators/` — Strategie rysowania adnotacji

Wzorzec Strategy — różne wizualizacje adnotacji na obrazie Qt.

### `annotator.py` — klasa `Annotator` (dispatcher)

Metoda statyczna `QtDraw()` deleguje rysowanie do odpowiedniej strategii na podstawie `AnnotatorType`:

```
AnnotatorType.Default        → AnnotatorDefault.Draw()
AnnotatorType.ConfidenceHeat → AnnotatorConfidenceHeat.Draw()
AnnotatorType.Category       → AnnotatorCategory.Draw()
```

### `annotator_default.py` — `AnnotatorDefault`

Domyślny styl:
- **Adnotacja ludzka** → czarny/żółty prostokąt (zielone kółko w rogu)
- **Detekcja** → zielony prostokąt z confidence `[0.85]`
- **Ręczna** → ciemnozielony prostokąt
- **FalseNegative** → czerwony prostokąt

### `annotator_confidence_heat.py` — `AnnotatorConfidenceHeat`

Heatmapa kolorów R-Y-G (red→yellow→green) na podstawie confidence:
- 0% → czerwony
- 50% → żółty
- 100% → zielony

Funkcja `RYG_color_as_rgb(value)` interpoluje kolor w skali 0–100.

### `annotator_category.py` — `AnnotatorCategory`

Kolorowanie adnotacji wg numeru klasy — cykliczna paleta matplotlib. Wizualnie rozróżnia obiekty różnych klas na jednym obrazie. Numeruje kolory modulo długość palety.
