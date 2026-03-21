# Specyfikacja Techniczna Projektu YAYA

> **YAYA — Yet Another YOLO Annoter**
> Desktopowa aplikacja (Python 3.11+ / PyQt5) do tworzenia, edycji i walidacji adnotacji bounding-box w formacie YOLO.

---

## Spis treści

1. [Cel i Architektura Systemu](#1-cel-i-architektura-systemu)
2. [Zarządzanie Konfiguracją i Artefaktami](#2-zarządzanie-konfiguracją-i-artefaktami)
3. [Modele Danych i Typowanie](#3-modele-danych-i-typowanie)
4. [Logika Biznesowa i Moduły](#4-logika-biznesowa-i-moduły)
5. [Przepływ Sterowania](#5-przepływ-sterowania)
6. [Strategia Testowania i Jakości](#6-strategia-testowania-i-jakości)

---

## 1. Cel i Architektura Systemu

### 1.1 Cel projektu

YAYA jest narzędziem dla inżynierów danych i badaczy Computer Vision, które umożliwia:

- **Ręczne tworzenie adnotacji** — rysowanie, edycja, usuwanie bounding-boxów na obrazach
- **Automatyczną detekcję obiektów** — integracja z detektorami YOLO (YOLOv4 Darknet, YOLOv5/v8/v11 Ultralytics, YOLO World)
- **Walidację adnotacji** — porównywanie wyników detektora z adnotacjami ręcznymi (metryki TP/FP/FN, Precision, Recall)
- **Analizę wizualną datasetu** — analiza HSV, rozmiarów obiektów, wyszukiwanie duplikatów (image hashing), rozkład klas
- **Zarządzanie datasetem** — filtrowanie plików, dataset treningowy/walidacyjny, eksport

### 1.2 Architektura wysokopoziomowa

Projekt **nie** stosuje konteneryzacji ani architektury mikrousługowej. Jest to **monolityczna aplikacja desktopowa** działająca jako pojedynczy proces na maszynie użytkownika.

```
┌─────────────────────────────────────────────────────────────────┐
│                      yolo-annotate.py                           │
│              (entry-point, argparse, boot)                      │
└───────┬─────────────────────┬───────────────────────────────────┘
        │                     │
  ┌─────▼──────┐    ┌────────▼─────────┐
  │ MainWindow │    │     Annoter      │
  │   (GUI)    │◄──►│  (engine core)   │
  └─────┬──────┘    └────────┬─────────┘
        │                    │
  ┌─────▼──────┐    ┌────────▼─────────┐
  │   Views    │    │   Detectors      │
  │  (tabele)  │    │ (YOLO backends)  │
  └────────────┘    └──────────────────┘
        │                    │
  ┌─────▼──────────────────▼───────────┐
  │          helpers/                   │
  │  (boxes, metrics, files, visuals)  │
  └─────────────────────────────────────┘
```

### 1.3 Warstwy architektury

| Warstwa | Katalogi | Odpowiedzialność |
|---------|----------|------------------|
| **Entry-point** | `yolo-annotate.py` | Parsowanie CLI, bootstrap detektora i annotera, uruchomienie GUI |
| **Kontroler GUI** | `MainWindow.py`, `ViewerEditorImage.py` | Kontroler głównego okna, interaktywny edytor bounding-boxów |
| **Widoki** | `views/` | Generowanie zawartości tabel QTableWidget (prezentacja danych) |
| **Silnik** | `engine/` | Logika domenowa: adnotacje, pliki, metryki, konfiguracja — **bez** zależności od PyQt5 |
| **Detektory** | `Detectors/` | Abstrakcja nad backendami detekcji YOLO (Darknet, OpenCV DNN, Ultralytics) |
| **Helpery** | `helpers/` | Narzędzia: bounding-boxy, NMS, pliki, metryki, rysowanie, kolory |
| **Widgety** | `Gui/` | Niestandardowe QTableWidgetItem, rysowanie OpenCV, stałe kolorów |
| **Dekoratory** | `Decorators/` | Generatory raportów i wizualizacji datasetu |
| **Modele** | `models/` | Struktury danych dla zewnętrznych integracji (np. klasyfikacja GPT) |

### 1.4 Separacja warstw

Kluczowa zasada architektoniczna: **logika biznesowa (`engine/`) nie zależy od PyQt5**. Pakiet `engine/` zawiera wyłącznie logikę przetwarzania adnotacji, plików i konfiguracji. Warstwa prezentacji (MainWindow, Views, Gui) deleguje wszystkie operacje domenowe do silnika.

Wyjątek stanowi `engine/annotators/`, który zawiera kod rysowania adnotacji na `QPainter` — jest to warstwa stylu wizualizacji (wzorzec Strategy), ale logika decyzyjna (np. ocena TP/FP/FN) pozostaje w silniku.

### 1.5 Środowisko uruchomieniowe

- **Język:** Python 3.11+
- **GUI:** PyQt5 5.15.7
- **Computer Vision:** OpenCV (headless) 4.7, NumPy <2.0
- **Detekcja:** Ultralytics >=8.3, opcjonalnie natywny Darknet (ctypes)
- **Analiza danych:** pandas, imagehash
- **System budowania:** pdm-backend
- **Menedżer pakietów:** `uv` (sync, add, run)

Projekt nie posiada Dockerfile ani konteneryzacji — jest uruchamiany bezpośrednio w środowisku Python.

---

## 2. Zarządzanie Konfiguracją i Artefaktami

### 2.1 Konfiguracja projektu (`pyproject.toml`)

Centralny plik konfiguracyjny projektu definiujący:

**Zależności runtime:**

| Pakiet | Wersja | Rola |
|--------|--------|------|
| `pyqt5` | 5.15.7 | Framework GUI |
| `opencv-python-headless` | 4.7.0.72 | Przetwarzanie obrazów, detekcja (DNN backend) |
| `numpy` | <2.0.0 | Operacje na tablicach, algebra |
| `pandas` | >=2.2.3 | Analiza danych, DataFrame |
| `ultralytics` | >=8.3.191 | Detektor YOLOv5/v8/v11 |
| `imagehash` | 4.3.1 | Perceptualny hashing obrazów (duplikaty) |
| `tqdm` | >=4.67.1 | Paski postępu |

**Zależności deweloperskie:**

| Narzędzie | Rola |
|-----------|------|
| `ruff` | Formatowanie + lint |
| `pyright` | Statyczna analiza typów (tryb `strict`) |
| `pytest` + `pytest-cov` | Framework testowy + pokrycie kodu |
| `pyqt5-stubs` | Type stubs dla PyQt5 |
| `isort` | Sortowanie importów |
| `taplo` | Formatowanie TOML |

**Konfiguracja narzędzi:**

- **Pyright:** `typeCheckingMode = "strict"` — pełna weryfikacja typów
- **Ruff:** `line-length = 120`, preview mode, szerokie reguły lint (E, F, B, Q, I, N, LOG, UP, RET, C4, ISC, PIE, RSE, SLOT, FAST, SIM, DOC)
- **Build system:** `pdm-backend`

### 2.2 Parametryzacja systemu (TOML)

System konfiguracji oparty jest o pliki TOML z mechanizmem fallback:

```
config.toml              ← konfiguracja użytkownika (opcjonalny)
config.example.toml      ← konfiguracja domyślna (fallback)
```

**Klasa `ConfigToml`** (`engine/config_toml.py`) implementuje wzorzec **Singleton** i zapewnia:

1. Próba wczytania `config.toml`
2. Jeśli nie istnieje → fallback do `config.example.toml`
3. Jeśli oba brakują → `FileNotFoundError`
4. Nieprawidłowy format TOML → natychmiastowe zakończenie (`sys.exit`)

**API konfiguracji:**

| Metoda | Zachowanie |
|--------|------------|
| `get(key, default)` | Bezpieczne pobranie z fallbackiem |
| `__getitem__(key)` | Pobranie lub `sys.exit` z komunikatem o brakującym kluczu |

**Struktura konfiguracji TOML:**

```toml
[detector]
detector = "Default"           # Default | YoloWorld
confidence = 0.25              # Próg confidence detekcji
nms = 0.45                     # Próg NMS
nms_method = "greedy"          # Nms | SoftNms | NmWeighted | WeightedBoxFusion
image_strategy = "resize"      # Rescale | LetterBox | Tiling2x2 | Tiling (SAHI)

[detector.ultralytics]
force_cpu = false              # Wymuszenie CPU
task = "detect"                # detect | segment | classify
half_precision = true          # FP16 inference
use_tensorrt = false           # TensorRT engine

[detector.yolo_world]
default_prompt = "warning lamp:lamp1, emergency light:lamp2"
```

Nadpisywanie lokalne realizowane jest przez obecność pliku `config.toml` w katalogu roboczym — użytkownik kopiuje `config.example.toml` i modyfikuje wybrane ustawienia.

### 2.3 Ustawienia użytkownika (QSettings)

Oprócz plików TOML, aplikacja przechowuje dane sesji użytkownika w systemowym rejestrze ustawień Qt (`QSettings`):

- **Historia otwartych katalogów** — stack do 64 ostatnio otwartych lokalizacji
- **Organizacja:** `AISP` / `aisp.pl` / `YAYA`

### 2.4 Zarządzanie artefaktami

Projekt **nie** używa Git LFS. Duże pliki binarne (wagi modeli `.weights`, `.pt`) nie są wersjonowane w repozytorium — należy je umieścić ręcznie w podkatalogach `Detectors/`.

**Konwencja katalogów modeli:**

```
Detectors/
├── <nazwa_modelu>/
│   ├── model.cfg        # Konfiguracja sieci (Darknet)
│   ├── model.weights    # Wagi sieci (Darknet)
│   ├── model.data       # Metadane (Darknet)
│   ├── model.names      # Nazwy klas
│   └── model.pt         # Wagi sieci (Ultralytics)
```

Fabryka `ListDetectors()` automatycznie skanuje podkatalogi `Detectors/` i wykrywa dostępne modele na podstawie rozszerzeń plików.

**Pliki towarzyszące obrazom (generowane w runtime):**

| Rozszerzenie | Opis |
|--------------|------|
| `.txt` | Adnotacje YOLO (classNumber x y w h) |
| `.detector` | Cache wyników detekcji (className confidence x y w h) |
| `.yoloworld` | Cache wyników YOLO World |
| `.visuals.json` | Właściwości wizualne (HSV grid, dhash, wymiary) |
| `dataset.txt` | Lista annotowanych plików w katalogu |
| `validation.txt` | Lista plików datasetu walidacyjnego |

### 2.5 Sesje (`Session`)

Dataclass `Session` umożliwia tworzenie snapshot'ów plików do katalogu `temp/session_YYYYMMDD_HHMM/`. Kopiowane są: obraz, adnotacje (`.txt`), detekcje (`.detector`), dane wizualne (`.visuals`).

---

## 3. Modele Danych i Typowanie

### 3.1 Podejście do typowania

Projekt stosuje **statyczną analizę typów** z Pyright w trybie `strict`. Obowiązują zasady:

- Wszystkie funkcje i metody mają adnotacje typów (argumenty + wartość zwracana)
- Nowoczesna składnia typów Python 3.10+ (`list[str]`, `str | None` zamiast `List[str]`, `Optional[str]`)
- `TYPE_CHECKING` jest **zabronionyimport musi być bezwarunkowy i dostępny w runtime
- Dla tablic NumPy używany jest alias `NumpyArray` z `helpers.aisp_typing`

### 3.2 Klasa `Annote` — Model adnotacji bounding-box

Centralna encja systemu — reprezentuje pojedynczą adnotację obiektu na obrazie.

**Lokalizacja:** `engine/annote.py` (316 linii)

| Pole | Typ | Opis |
|------|-----|------|
| `box` | `tuple[float, float, float, float]` | Bounding-box znormalizowany (x1, y1, x2, y2) w formacie xyxy, zakres 0–1 |
| `classNumber` | `int` | Numer klasy obiektu |
| `className` | `str` | Nazwa klasy obiektu |
| `confidence` | `float` | Pewność detekcji (0–100) |
| `authorType` | `AnnoteAuthorType` | Kto utworzył adnotację (człowiek/detektor/ręcznie) |
| `evalution` | `AnnoteEvaluation` | Wynik ewaluacji (TP/FN/brak) |
| `evaluation_iou` | `float` | IOU z najlepszym dopasowaniem |
| `evaluation_confidence` | `float` | Confidence dopasowanej detekcji |
| `evaluation_class_id` | `int` | ID klasy z ewaluacji (-1 = brak) |
| `hue` | `float` | Wartość H z HSV wycinka obrazu |
| `saturation` | `float` | Wartość S z HSV wycinka obrazu |
| `brightness` | `float` | Wartość V z HSV wycinka obrazu |

**Properties obliczeniowe:**

| Property | Typ zwracany | Opis |
|----------|-------------|------|
| `width` | `float` | Szerokość bboxa (znormalizowana) |
| `height` | `float` | Wysokość bboxa (znormalizowana) |
| `area` | `float` | Powierzchnia bboxa (znormalizowana) |
| `ratio` | `float` | Stosunek szerokości do wysokości |
| `class_abbrev` | `str` | Skrót nazwy klasy (max 3 litery, uppercase) |
| `evaluation_class_name` | `str` | Nazwa klasy z ewaluacji |

**Serializacja/deserializacja:**

| Funkcja modułowa | Kierunek | Opis |
|-------------------|----------|------|
| `toTxtAnnote(annote)` | Annote → tuple | Konwersja do formatu pliku `.txt` (classNumber, box) |
| `fromTxtAnnote(txt)` | tuple → Annote | Tworzenie z rekordu pliku `.txt` |
| `toYoloDetection(annote)` | Annote → tuple | Konwersja do (className, 100, box) |
| `fromDetection(detection)` | tuple → Annote | Tworzenie z detekcji (className, confidence, box) |

**Globalna lista klas:**

Moduł `annote.py` przechowuje globalną listę nazw klas (`classNames`) inicjalizowaną przez `Init(names)`. Funkcje `GetClasses()`, `GetClassName(number)`, `GetClassNumber(name)` operują na tej liście.

### 3.3 Enumy (`annote_enums.py`)

**`AnnoteAuthorType`** — Kto utworzył adnotację:

| Wartość | Opis |
|---------|------|
| `byHuman` (0) | Adnotacja wczytana z pliku `.txt` (uznawana za ludzką) |
| `byDetector` (1) | Adnotacja wygenerowana przez detektor YOLO |
| `byHand` (2) | Adnotacja narysowana ręcznie w bieżącej sesji edycji |

**`AnnoteEvaluation`** — Wynik ewaluacji:

| Wartość | Opis |
|---------|------|
| `noEvaluation` (0) | Brak ewaluacji (np. brak detektora) |
| `TruePositiveLabel` (1) | Bbox + klasa dopasowane poprawnie |
| `TruePositive` (2) | Bbox dopasowany, ale klasa inna |
| `FalseNegative` (3) | Adnotacja niepokryta detekcją |

**`AnnotatorType`** — Styl wizualizacji:

| Wartość | Opis |
|---------|------|
| `Default` | Standardowe prostokąty z kolorami zależnymi od autora/ewaluacji |
| `ConfidenceHeat` | Mapa cieplna bazująca na confidence |
| `Category` | Kolory bazujące na numerze klasy (paleta matplotlib) |

### 3.4 Dataclass `Metrics` — Metryki ewaluacji

**Lokalizacja:** `helpers/metrics.py` (325 linii)

| Pole | Typ | Domyślna | Opis |
|------|-----|----------|------|
| `All` | `int` | 0 | Liczba wszystkich adnotacji |
| `AvgWidth` | `float` | -1.0 | Średnia szerokość adnotacji |
| `AvgHeight` | `float` | -1.0 | Średnia wysokość adnotacji |
| `iou_avg` | `float` | 0.0 | Średnie najlepsze IOU |
| `overlapping_iou` | `float` | 0.0 | IOU nakładania się adnotacji |
| `TP` | `int` | 0 | True Positives (bbox dopasowany) |
| `FP` | `int` | 0 | False Positives (detekcja bez adnotacji) |
| `TN` | `int` | 0 | True Negatives (nieużywane w object detection) |
| `FN` | `int` | 0 | False Negatives (adnotacja bez detekcji) |
| `LTP` | `int` | 0 | Label True Positives (bbox + klasa) |
| `detections` | `list` | `[]` | Lista wszystkich detekcji |
| `new_detections` | `list` | `[]` | Lista nowych (niedopasowanych) detekcji |
| `matches` | `list` | `[]` | Lista par (annotation, detection) |

**Properties obliczeniowe:** `correct`, `correct_bboxes`, `precision`, `recall`, `mAP`, `AvgSize`, `detections_confidence`, `detections_confidence_min`, `matches_confidence`.

Mutowalne pola (listy) używają `default_factory=list` — zapobiega to współdzieleniu stanu między instancjami.

### 3.5 Dataclass `Visuals` — Właściwości wizualne obrazu

**Lokalizacja:** `helpers/visuals.py` (198 linii)

| Pole | Typ | Opis |
|------|-----|------|
| `imagepath` | `str` | Ścieżka do obrazu |
| `width` | `float` | Szerokość obrazu |
| `height` | `float` | Wysokość obrazu |
| `grid` | `list[tuple[float, float, float]]` | Siatka 20×20 wartości HSV |
| `dhash` | `str` | Perceptualny hash obrazu (imagehash) |
| `isDuplicate` | `bool` | Flaga duplikatu |

**Wzorzec fabrykujący:** `Visuals.LoadCreate(imagepath, force)` — ładuje z cache JSON lub tworzy nowy obiekt i zapisuje. Łańcuch: Load → (brak) → Create → Save.

**Serializacja:** `dataclasses.asdict()` → JSON (`helpers.json.jsonWrite/jsonRead`).

### 3.6 Dataclass `AnnotationsClassifiedBool` — Wyniki klasyfikacji zewnętrznej

**Lokalizacja:** `models/annotations_classified.py` (123 linie)

Przechowuje wyniki binarnej klasyfikacji adnotacji (np. z GPT). Wszystkie pola to tablice NumPy:

| Pole | Typ NumPy | Opis |
|------|-----------|------|
| `filenames` | `NDArray[np.str_]` | Nazwy plików |
| `class_ids` | `NDArray[np.int16]` | ID klas |
| `x`, `y`, `w`, `h` | `NDArray[np.float32]` | Współrzędne bboxów |
| `bools` | `NDArray[np.bool_]` | Wynik klasyfikacji True/False |

Każde pole posiada `default_factory=lambda: np.array([], dtype=...)` — zapobiega współdzieleniu tablic między instancjami.

**Serializacja:** `from_csv(path)` → pandas `read_csv` → NumPy arrays; `to_csv(path)` → pandas DataFrame → CSV.

### 3.7 Dataclass `Detection` — Surowa detekcja z YOLO HEAD

**Lokalizacja:** `Detectors/common/Detection.py` (79 linii)

| Pole | Typ | Opis |
|------|-----|------|
| `xywh` | `list[float]` | Bounding-box w formacie center (x, y, w, h) |
| `objectness` | `float` | Wartość objectness z YOLO HEAD |
| `probabilities` | `list[float]` | Prawdopodobieństwa dla każdej klasy |

**Properties:** `confidence` (max z probabilities), `class_id` (argmax z probabilities), `class_label` (nazwa klasy).

### 3.8 Dataclass `Session` — Sesja programu

**Lokalizacja:** `engine/session.py`

| Pole | Typ | Opis |
|------|-----|------|
| `timestamp` | `datetime` | Czas rozpoczęcia sesji (`default_factory=datetime.now`) |

**Property:** `session_path` → `temp/session_YYYYMMDD_HHMM/`.

### 3.9 Klasa `Dataset` — Zbiór ścieżek plików

**Lokalizacja:** `engine/dataset.py` (105 linii)

| Pole | Typ | Opis |
|------|-----|------|
| `_path` | `str | None` | Ścieżka do pliku dataset |
| `_dataset` | `set[str]` | Zbiór nazw plików |
| `_is_not_saved` | `bool` | Flaga niezapisanych zmian |

### 3.10 Klasa `BoxState` — Stan okluzji bounding-boxu

**Lokalizacja:** `helpers/boxes.py`

Bitmaskowy enum stanów:

| Bit | Stała | Opis |
|-----|-------|------|
| 0x00 | `Isolated` | Box izolowany |
| 0x01 | `Occluding` | Box zasłaniający inny |
| 0x02 | `Occluded` | Box zasłonięty |
| 0x04 | `Containing` | Box zawierający inny |
| 0x08 | `Contained` | Box zawarty w innym |

### 3.11 Struktura `fileEntry` — Słownik danych pliku

Struktura `dict` przepływająca przez system (generowana w `Annoter.OpenLocation()`):

| Klucz | Typ | Opis |
|-------|-----|------|
| `Name` | `str` | Nazwa pliku obrazu |
| `Path` | `str` | Pełna ścieżka do pliku |
| `ID` | `int` | Indeks w oryginalnej liście plików |
| `IsAnnotation` | `bool` | Czy istnieje plik adnotacji `.txt` |
| `IsValidation` | `bool` | Czy plik jest w zbiorze walidacyjnym |
| `Annotations` | `list[Annote]` | Lista adnotacji ludzkich |
| `AnnotationsClasses` | `str` | Skróty klas adnotacji (CSV) |
| `Datetime` | `float` | Timestamp modyfikacji pliku |
| `Errors` | `int` | Liczba błędów |
| `Detections` | `list[Annote]` | Detekcje (po filtracji IOU) |
| `Detections_original` | `list[Annote]` | Detekcje (oryginalne, bez filtracji) |
| `Metrics` | `Metrics` | Metryki ewaluacji |
| `Visuals` | `Visuals` | Właściwości wizualne |

### 3.12 Formaty bounding-boxów

System operuje na trzech formatach współrzędnych:

| Format | Struktura | Zakres | Użycie |
|--------|-----------|--------|--------|
| **YOLO (Bbox/xywh)** | `(center_x, center_y, width, height)` | 0–1 | Pliki `.txt`, detekcje |
| **Rect (xyxy)** | `(x1, y1, x2, y2)` | 0–1 | Wewnętrzna reprezentacja w `Annote.box` |
| **Absolute (xyxy px)** | `(x1, y1, x2, y2)` | piksele | Rysowanie na obrazie |

**Konwersje** (`helpers/boxes.py`):
- `Bbox2Rect()` / `Rect2Bbox()` — YOLO ↔ xyxy (znormalizowane)
- `ToAbsolute()` / `ToRelative()` — znormalizowane ↔ piksele
- `to_xyxy()` — YOLO → xyxy (alias)

---

## 4. Logika Biznesowa i Moduły

### 4.1 Moduł `engine/` — Rdzeń aplikacji

#### 4.1.1 `Annoter` — Główny silnik adnotacji

**Lokalizacja:** `engine/annoter.py` (840 linii)

Centralny komponent logiki biznesowej. Nie zależy od PyQt5.

**Odpowiedzialność:**
- Zarządzanie listą plików obrazów w katalogu (skanowanie, sortowanie, nawigacja, filtrowanie)
- Integracja z detektorami YOLO (uruchamianie, cache wyników)
- Ładowanie/zapisywanie adnotacji i detekcji (pliki `.txt`, `.detector`)
- Ewaluacja metryk TP/FP/FN/Precision/Recall
- Cache właściwości wizualnych (HSV, dhash) per obraz
- Wykrywanie duplikatów obrazów
- Zarządzanie datasetem treningowym i walidacyjnym

**Wejście:**
- `filepath` — ścieżka do katalogu z obrazami
- `detector` — instancja detektora YOLO (lub None)
- Parametry konfiguracyjne: `detectorConfidence`, `detectorNms`, flagi filtrów

**Wyjście:**
- `self.files` — lista `fileEntry` dict'ów z pełnymi danymi per obraz
- `self.annotations` — adnotacje bieżącego pliku (łączone: ludzkie + detekcje)
- `self.image` — bieżący obraz cv2

**Metody sortowania:**

| Stała | Opis |
|-------|------|
| `NoSort` | Bez sortowania |
| `SortByDatetime` | Chronologicznie (najstarsze pierwsze) |
| `SortByInvDatetime` | Chronologicznie odwrócone (najnowsze pierwsze — domyślne) |
| `SortByAlphabet` | Alfabetycznie |

**Filtry (stosowane przy `OpenLocation`):**

| Flaga | Efekt |
|-------|-------|
| `isOnlyNewFiles` | Tylko pliki bez adnotacji |
| `isOnlyOldFiles` | Tylko pliki z adnotacjami |
| `isOnlyErrorFiles` | Tylko pliki z błędami |
| `isOnlySpecificClass` | Tylko pliki z konkretną klasą |

**Kluczowe metody:**

| Metoda | Opis |
|--------|------|
| `OpenLocation(path)` | Skanowanie katalogu, ładowanie wszystkich plików z adnotacjami/detekcjami/wizualizacjami |
| `Process()` | Przetworzenie bieżącego pliku (obraz, adnotacje, detekcje, metryki) |
| `ProcessNext()` / `ProcessPrev()` | Nawigacja i przetwarzanie następnego/poprzedniego pliku |
| `Save()` | Zapis adnotacji bieżącego pliku do `.txt` |
| `AddAnnotation(box, classNumber)` | Dodanie nowej adnotacji |
| `RemoveAnnotation(element)` | Usunięcie adnotacji |
| `Delete()` | Usunięcie pliku obrazu i adnotacji |
| `ProcessDetections(im, filepath)` | Uruchomienie detekcji (deleguje do odpowiedniego detektora) |
| `CalculateYoloMetrics(annotations, detections)` | Obliczenie metryk |
| `GetFiles(filter_*_classnames)` | Pobranie listy plików z filtrowaniem po klasach |

#### 4.1.2 `annote.py` — Model adnotacji

Szczegółowy opis → sekcja 3.2.

#### 4.1.3 `config_toml.py` — Konfiguracja TOML (Singleton)

Szczegółowy opis → sekcja 2.2.

#### 4.1.4 `dataset.py` — Zarządzanie zbiorami danych

Zarządza plikami `dataset.txt` i `validation.txt`:

| Metoda | Opis |
|--------|------|
| `add(path)` | Dodaje ścieżkę do zbioru (z guard clause na duplikat) |
| `remove(path)` | Usuwa ścieżkę ze zbioru (z guard clause na brak) |
| `load(path)` | Wczytuje plik, waliduje istnienie plików, auto-usuwa nieistniejące |
| `save()` | Zapisuje posortowane ścieżki do pliku |
| `is_inside(path)` | Sprawdza przynależność do zbioru |

#### 4.1.5 `session.py` — Snapshoty plików

Kopiuje bieżący obraz i powiązane pliki do `temp/session_YYYYMMDD_HHMM/`.

#### 4.1.6 `GuiClassKeycodes` — Mapowanie klawiszy

Mapuje klawisze klawiatury (`1`–`0`, `-`, `=`, `` ` ``) na numery klas. Klawisz `` ` `` służy jako modyfikator offset'u (przesunięcie o 12 klas), umożliwiając obsługę > 12 klas.

#### 4.1.7 `annotators/` — Strategie wizualizacji (Strategy Pattern)

**Dispatcher:** `Annotator.QtDraw()` — deleguje rysowanie do odpowiedniej strategii na podstawie `AnnotatorType`.

| Strategia | Klasa | Logika kolorowania |
|-----------|-------|-------------------|
| Default | `AnnotatorDefault` | Kolor zależy od `authorType` i `evaluation` (czarny/żółty/czerwony/zielony) |
| ConfidenceHeat | `AnnotatorConfidenceHeat` | Kolor zależy od wartości confidence |
| Category | `AnnotatorCategory` | Kolor zależy od numeru klasy (paleta matplotlib) |

### 4.2 Moduł `Detectors/` — Warstwa detekcji

#### 4.2.1 Fabryka detektorów (`__init__.py`)

| Funkcja | Opis |
|---------|------|
| `ListDetectors(path)` | Skanuje podkatalogi w poszukiwaniu modeli (.cfg+.weights+.names lub .pt+.names) |
| `CreateDetector(detectorID, gpuID)` | Tworzy instancję detektora na podstawie indeksu |
| `GetDetectorLabels(detectorID)` | Zwraca nazwy klas bez inicjalizacji detektora |
| `IsDarknet()` | Sprawdza obecność `/usr/local/lib/libdarknet.so` |

**`DetectorType` enum:**

| Wartość | Backend |
|---------|---------|
| `Darknet` | Natywna biblioteka Darknet (ctypes, `libdarknet.so`) |
| `CVDNN` | OpenCV DNN backend |
| `Ultralytics` | Ultralytics SDK (YOLOv5/v8/v11) |

#### 4.2.2 Klasa bazowa `Detector`

**Lokalizacja:** `Detectors/common/Detector.py` (160 linii)

| Metoda | Opis |
|--------|------|
| `Init()` | Inicjalizacja po utworzeniu |
| `Detect(frame, confidence, nms_thresh, ...)` | Detekcja → lista `(label, confidence, box)` |
| `Close()` | Zwolnienie zasobów |
| `EnsembleBoxes(boxes, scores, classids, ...)` | Statyczna — filtrowanie NMS z wyborem metody |
| `ToDetections(boxes, scores, classids)` | Konwersja surowych danych na listę krotek |
| `GetClassNames()` | Lista nazw klas |
| `Draw(image, detections)` | Rysowanie detekcji na obrazie (OpenCV) |

**`NmsMethod` enum:**

| Wartość | Algorytm | Źródło |
|---------|----------|--------|
| `Nms` | Klasyczny Non-Maximum Suppression | `ensemble_boxes_nms.py` |
| `SoftNms` | Soft-NMS (wygładzanie confidence) | `ensemble_boxes_nms.py` |
| `NmWeighted` | Non-Maximum Weighted (uśrednianie boxów) | `ensemble_boxes_nmw.py` |
| `WeightedBoxFusion` | Weighted Boxes Fusion (ensemble) | `ensemble_boxes_wbf.py` |

#### 4.2.3 Implementacje detektorów

| Detektor | Klasa | Backend | Wymagania |
|----------|-------|---------|-----------|
| **YOLOv4 Darknet** | `DetectorYOLOv4` (490 linii) | `libdarknet.so` (ctypes) | Kompilacja natywnego Darknet |
| **YOLOv4 OpenCV DNN** | `DetectorCVDNN` (225 linii) | `cv2.dnn.readNetFromDarknet()` | Brak — czysty OpenCV |
| **YOLOv5/v8/v11** | `DetectorYolov8` (300 linii) | Ultralytics SDK | `pip install ultralytics` |

**`ImageStrategy` enum** — strategia przetwarzania obrazu wejściowego:

| Wartość | Opis |
|---------|------|
| `Rescale` | Przeskalowanie do rozmiaru sieci |
| `RescaleNearest` | Przeskalowanie algorytmem nearest-neighbor |
| `LetterBox` | LetterBox (zachowanie proporcji + padding) |
| `Tiling2x2` | Podzielenie na 4 kafelki 2×2 |
| `Tiling` | Tiling SAHI (adaptacyjny podział) |

### 4.3 Moduł `helpers/` — Biblioteka narzędzi

#### 4.3.1 Bounding-boxy i NMS

| Moduł | Linie | Opis |
|-------|-------|------|
| `boxes.py` | 384 | Konwersje formatów, IOU, geometria, okluzje |
| `ensemble_boxes_nms.py` | 259 | Klasyczny NMS + Soft-NMS (ZFTurbo) |
| `ensemble_boxes_nmw.py` | 177 | Non-Maximum Weighted |
| `ensemble_boxes_wbf.py` | 180 | Weighted Boxes Fusion |
| `soft_nms.py` | 122 | Alternatywna implementacja Soft-NMS |
| `prefilters.py` | — | Filtr pre-NMS (IOU + confidence) |
| `detections.py` | — | Scalanie detekcji z kafelków |

#### 4.3.2 Pliki i adnotacje

| Moduł | Opis |
|-------|------|
| `files.py` | Ścieżki, rozszerzenia, tworzenie katalogów, SHA-1 nazwy |
| `textAnnotations.py` | Odczyt/zapis plików `.txt` i `.detector` w formacie YOLO |
| `json.py` | JSON z obsługą dataclass/datetime |
| `hashing.py` | SHA-1 dla nazw plików |

#### 4.3.3 Analiza obrazów

| Moduł | Opis |
|-------|------|
| `visuals.py` | Właściwości wizualne (HSV grid 20×20, dhash, duplikaty) |
| `images.py` | Skalowanie obrazów z zachowaniem proporcji |
| `colors.py` | Stałe kolorów BGR, schematy (Bright, Matplotlib), `ColorCycler` |
| `transformations.py` | Transformacje obrazu (flip, augmentacja) |

#### 4.3.4 Metryki i algebra

| Moduł | Opis |
|-------|------|
| `metrics.py` | Ewaluacja TP/FP/FN/Precision/Recall/mAP |
| `algebra.py` | Geometria 2D (odległość euklidesowa, translacja, kąty) |

#### 4.3.5 Infrastruktura

| Moduł | Opis |
|-------|------|
| `Singleton.py` | Metaklasa Singleton (używana przez `ConfigToml`) |
| `gpu.py` | Detekcja CUDA/GPU, info o systemie |
| `git.py` | Informacje z Git (tag, branch, hash) |
| `MarkdownReport.py` | Generator raportów Markdown |
| `QtDrawing.py` | Prymitywy rysowania Qt (`QPainter`): prostokąty, elipsy, tekst, krzyżyki |

### 4.4 Warstwa prezentacji

#### 4.4.1 `MainWindowGui` — Kontroler głównego okna

**Lokalizacja:** `MainWindow.py` (1006 linii)

Klasa dziedzicząca `Ui_MainWindow` (auto-generowany layout). Centralny kontroler GUI łączący silnik z interfejsem.

**Zarządza:**
- `self.annoter` — instancja `Annoter` (logika biznesowa)
- `ViewerEditorImage` — widget edytora obrazu
- Widoki tabel: `ViewImagesTable`, `ViewAnnotations`, `ViewDetections`, `ViewFilters`, `ViewImagesSummary`
- `self.session` — snapshoty plików
- `self.gpt_annotations_classified` — wyniki klasyfikacji GPT
- `self.system_settings` — `QSettings` (historia katalogów)

**Kluczowe metody:**

| Metoda | Opis |
|--------|------|
| `LocationOpen(path)` | Otwiera katalog z obrazami → deleguje do `Annoter.OpenLocation()` |
| `SetupCallbacks()` | Podpięcie sygnałów Qt do callbacków |
| `SetupDefault()` | Ustawienia domyślne UI |
| `OpenedDirectoriesStore/Get()` | Historia otwartych katalogów (QSettings) |
| `ImageIDToRowNumber()` / `RowNumberToImageID()` | Mapowanie wierszy tabeli ↔ ID plików |
| `Run()` | Uruchomienie pętli zdarzeń Qt (`app.exec()`) |

#### 4.4.2 `ViewerEditorImage` — Interaktywny edytor obrazu

**Lokalizacja:** `ViewerEditorImage.py` (775 linii)

Widget Qt (`QWidget`) służący jako edytor bounding-boxów.

**Tryby edycji:**

| Tryb | Stała | Opis |
|------|-------|------|
| Brak | `ModeNone` | Nawigacja / podgląd |
| Dodawanie | `ModeAddAnnotation` | Rysowanie nowego bboxa (LPM) |
| Usuwanie | `ModeRemoveAnnotation` | Usuwanie adnotacji (PPM) |
| Zmiana klasy | `ModeRenameAnnotation` | Zmiana numeru klasy |
| Malowanie | `ModePaintCircle` | Malowanie kółkiem na obrazie |

**Skalowanie obrazu:**

| Tryb | Opis |
|------|------|
| `ImageScalingResize` | Dopasowanie do widgetu |
| `ImageScalingResizeAspectRatio` | Dopasowanie z zachowaniem proporcji |
| `ImageScalingOriginalSize` | Oryginalny rozmiar 1:1 |
| `ImageScalingDynamicZoom` | Dynamiczny zoom (scroll) z panningiem |

**Transformacje wizualne:** threshold, sharpen, CLAHE, kontrast.

**Sygnały Qt:** `signalEditorFinished(int)` — emitowany po zakończeniu rysowania adnotacji.

#### 4.4.3 Widoki tabel (`views/`)

Klasy statyczne generujące zawartość `QTableWidget`. Wzorzec: widok przyjmuje pustą tabelę + dane → wypełnia kolumny odpowiednimi widgetami z `Gui/widgets/`.

| Widok | Plik | Opis |
|-------|------|------|
| `ViewImagesTable` | 294 linii | Główna tabela plików (19 kolumn: miniaturka, wymiary, adnotacje, metryki, HSV, hash) |
| `ViewAnnotations` | 176 linii | Tabela adnotacji ludzkich (11 kolumn: crop, klasa, confidence, ewaluacja, rozmiar, HSV) |
| `ViewDetections` | 199 linii | Tabela detekcji (analogiczna do ViewAnnotations, ale dla detekcji detektora) |
| `ViewFilters` | 140 linii | Grid przycisków filtrujących po klasach |
| `ViewImagesSummary` | — | Podsumowanie metryczne |

#### 4.4.4 Widgety tabelowe (`Gui/widgets/`)

Niestandardowe `QTableWidgetItem` z poprawnym sortowaniem numerycznym i wizualnym feedbackiem:

| Widget | Opis |
|--------|------|
| `ImageTableWidgetItem` | Miniaturka obrazu + tooltip HTML, cache (deque max 100) |
| `AnnotationsTableWidgetItem` | Lista klas z liczbą wystąpień |
| `BoolTableWidgetItem` | Zielone/czerwone tło + "Yes"/"No" |
| `EvalTableWidgetItem` | Kolor tła zależny od ewaluacji |
| `FloatTableWidgetItem` | Konfigurowalna precyzja, sortowanie numeryczne |
| `HsvTableWidgetItem` | Kolor tła z HSV, auto-kontrast tekstu |
| `ImhashTableWidgetItem` | Duplikaty: czerwone tło + prefix "[D]" |
| `PercentTableWidgetItem` | Skala barw R→Y→G, sortowanie numeryczne |
| `RectTableWidgetItem` | Wymiary W×H, sortowanie po powierzchni |
| `StatTableWidgetItem` | Timestamp "YYYY-MM-DD HH:MM:SS", sortowanie chronologiczne |

### 4.5 Moduł `Decorators/` — Analiza datasetu

#### 4.5.1 `DecoratorDistributionShowcase`

Generator raportu rozkładu klas w datasecie:

1. Dla każdej kategorii wybiera do 9 reprezentatywnych adnotacji (filtr po medianie rozmiaru)
2. Wycina fragmenty obrazów (crop bboxów) → zapisuje jako PNG
3. Tworzy raport Markdown z mozaikami per kategoria + statystykami

### 4.6 Moduł `models/` — Zewnętrzne integracje

Zawiera struktury danych dla zewnętrznych klasyfikatorów (np. GPT). Jedyny model: `AnnotationsClassifiedBool` (sekcja 3.6).

---

## 5. Przepływ Sterowania

### 5.1 Sekwencja startu aplikacji

```
yolo-annotate.py main()
    │
    ├── 1. argparse: --input, --detector, --detectorConfidence, --detectorNms,
    │                --noDetector, --forceDetector, --verbose
    │
    ├── 2. logging.basicConfig(DEBUG jeśli __debug__, inaczej INFO)
    │
    ├── 3. ListDetectors() → skanowanie Detectors/ po .cfg/.pt
    │   ├── Brak detektorów → noDetector = True, annote.Init(labels z .names)
    │   └── Znaleziono → CreateDetector() → detector.Init() → annote.Init(classNames)
    │
    ├── 4. Normalizacja ścieżki: FixPath(GetFileLocation(args.input))
    │
    ├── 5. [opcjonalnie] --forceDetector → usunięcie .detector i .json
    │
    ├── 6. Annoter(filepath, detector, ...) → OpenLocation() → skanowanie plików
    │
    └── 7. MainWindowGui(args, detector, annoter) → gui.Run() → QApplication.exec()
```

### 5.2 Przepływ otwierania lokalizacji

```
MainWindowGui.LocationOpen(path)
    │
    └── Annoter.OpenLocation(path)
            │
            ├── Walidacja ścieżki (guard clauses: None, pusta, nieistniejąca, ta sama)
            │
            ├── os.listdir() → filtrowanie obrazów (IsImageFile)
            │
            ├── Dataset.load("validation.txt")
            │
            ├── VisualsDuplicates() — inicjalizacja detektora duplikatów
            │
            └── FOR each file (z tqdm progress bar):
                    ├── IsExistsAnnotations() → ReadAnnotations() → [Annote]
                    ├── [forceDetector] → cv2.imread → ProcessDetections() → SaveDetections()
                    │   [else] → ReadDetections() z cache .detector
                    ├── EvaluateMetrics(annotations, detections)
                    ├── prefilters.filter_iou_by_confidence() → filtrowanie detekcji
                    ├── Visuals.LoadCreate() → HSV grid + dhash
                    ├── VisualsDuplicates.IsDuplicate() & Add()
                    ├── annote.update_hsv_from_grid() per adnotacja
                    └── files.append(fileEntry dict)
```

### 5.3 Przepływ przetwarzania bieżącego pliku

```
Annoter.Process()
    │
    ├── GetFileImage() → cv2.imread
    │
    ├── Visuals.Create() → aktualizacja danych wizualnych
    │
    ├── GetFileAnnotations() → ReadAnnotations() → [Annote]
    │
    ├── [detector enabled] → cv2.cvtColor(BGR→RGB)
    │   ├── ProcessDetections() → Detect() + SaveDetections()
    │   ├── CalculateYoloMetrics()
    │   └── prefilters.filter_iou_by_confidence()
    │
    └── self.annotations = txtAnnotations + detAnnotes
```

### 5.4 Przepływ ewaluacji metryk

```
EvaluateMetrics(annotations, detections, minConfidence=0.5, minIOU=0.5)
    │
    ├── Guard: brak adnotacji → Metrics(FP=len(detections))
    ├── Guard: brak detekcji → Metrics(All=len(annotations))
    │
    ├── Filtr confidence > minConfidence
    │
    ├── Obliczenie overlapping_iou (nakładanie adnotacji między sobą)
    │
    └── FOR each annotation:
            ├── IOU z każdą detekcją → sortowanie malejąco
            ├── iou_best < minIOU → FalseNegative
            ├── iou_best ≥ minIOU + klasa zgodna → TruePositiveLabel
            ├── iou_best ≥ minIOU + klasa inna → TruePositive
            └── Usunięcie dopasowanej detekcji z puli
```

### 5.5 Przepływ NMS (Non-Maximum Suppression)

```
Detector.EnsembleBoxes(boxes, scores, classids, nmsMethod, ...)
    │
    ├── NmsMethod.Nms          → nms() z ensemble_boxes_nms.py
    ├── NmsMethod.SoftNms      → soft_nms() z ensemble_boxes_nms.py
    ├── NmsMethod.NmWeighted   → non_maximum_weighted() z ensemble_boxes_nmw.py
    └── NmsMethod.WeightedBoxFusion → weighted_boxes_fusion() z ensemble_boxes_wbf.py
```

### 5.6 Hierarchiczne logowanie

Projekt stosuje standardowy moduł `logging` Pythona:

- **Konfiguracja globalna:** `logging.basicConfig()` w `yolo-annotate.py` (DEBUG w trybie debug, INFO w produkcji)
- **Loggery per moduł:** `logger = logging.getLogger(__name__)` (w nowszych modułach) lub bezpośrednio `logging.*()` (w starszym kodzie)
- **Poziomy używane w projekcie:**
  - `DEBUG` — szczegóły operacji (np. dodanie/zapis adnotacji)
  - `INFO` — istotne zdarzenia (otwarcie lokalizacji, znalezienie detektora, zapis pliku)
  - `WARNING` — brak detektorów, nieistniejące pliki w datasecie
  - `ERROR` — nieistniejące ścieżki, nieprawidłowe nazwy klas, błędy zapisu
  - `FATAL/CRITICAL` — błędy cv2 przy odczycie obrazu, duplikaty rejestracji

### 5.7 Obsługa warunków brzegowych

Projekt stosuje zasady **guard clauses** i **graceful degradation**:

**Guard clauses (wczesne wyjścia):**

```python
# Przykład z Annoter.OpenLocation():
if (path is None) or (len(path) == 0):
    logging.error("(Annoter) Path `%s` not exists!", path)
    return

if not os.path.exists(path):
    logging.error("(Annoter) Path `%s` not exists!", path)
    return

if self.dirpath == path:
    logging.info("(Annoter) Path `%s` is same!", path)
    return
```

**Graceful degradation:**

- Brak detektora → `noDetector = True`, aplikacja działa bez automatycznej detekcji
- Nieistniejący plik w datasecie → auto-usunięcie wpisu, kontynuacja
- Błąd cv2 przy odczycie obrazu → `logging.fatal()`, zwrot `None`
- Brak pliku konfiguracyjnego → fallback do `config.example.toml`
- Duplikat w zbiorze → `logging.error()` + return (bez wyjątku)

**Walidacja adnotacji:**

Metoda `__checkOfErrors()` w `Annoter` sprawdza nakładanie się adnotacji (overlapping) używając `prefilters.filter_iou_by_confidence()`. Wykryte błędy przechowywane są w `self.errors` (set stringów).

---

## 6. Strategia Testowania i Jakości

### 6.1 Framework testowy

- **Framework:** `pytest` (bez klas `unittest`)
- **Lokalizacja:** `tests/`
- **Uruchamianie:** `uv run pytest -m "not manual and not gpu and not benchmark" -v`

### 6.2 Kategoryzacja testów (markery pytest)

| Marker | Opis | Przykład |
|--------|------|---------|
| *(brak)* | Testy jednostkowe — uruchamiane w CI | `test_boxes.py` |
| `benchmark` | Testy wydajnościowe — nie w CI | `test_benchmark_nms.py` |
| `gpu` | Testy wymagające CUDA/GPU | `test_gpu.py` |
| `manual` | Testy integracyjne wymagające zewnętrznych zasobów | `test_yolo_world.py` |

**Domyślny filtr CI:** `-m "not manual and not gpu and not benchmark"`

### 6.3 Pliki testowe

| Plik | Typ | Co testuje |
|------|-----|------------|
| `test_boxes.py` | Jednostkowy | `helpers.boxes.tiles_iou()` — IOU kafelków: identyczne, sąsiadujące, oddzielne, różne rozmiary |
| `test_benchmark_nms.py` | Benchmark | Wydajność 4 metod NMS (time + FPS) na losowych detekcjach |
| `test_gpu.py` | GPU | Dostępność CUDA (`CudaDeviceLowestMemory()`), skip jeśli brak GPU |
| `test_yolo_world.py` | Integracyjny | YOLO World: detekcja klas tekstowych na obrazie testowym |

### 6.4 Strategia mockowania

Projekt stosuje `MagicMock` z `unittest.mock` dla złożonych zależności. W testach jednostkowych (np. `test_boxes.py`) testowana jest logika bezpośrednio bez potrzeby mockowania, ponieważ helpery (`boxes`, `metrics`) nie mają zależności zewnętrznych wymagających symulacji.

Dane testowe dla `test_yolo_world.py` przechowywane są w katalogu `tests/yolo_world/`.

### 6.5 Analiza statyczna i formatowanie

| Narzędzie | Konfiguracja | Rola |
|-----------|-------------|------|
| **Pyright** | `strict` mode | Statyczna analiza typów — pełna weryfikacja |
| **Ruff format** | `line-length = 120` | Formatowanie kodu |
| **Ruff lint** | Preview mode, 18 grup reguł | Lint: błędy (E), pyflakes (F), bugbear (B), cudzysłowy (Q), importy (I), nazewnictwo (N), logging (LOG), modernizacja (UP), return (RET), comprehensions (C4), implicit string concat (ISC), uproszczenia (SIM), docstringi (DOC) |

**Komendy walidacji:**

```bash
ruff format --check          # Sprawdzenie formatowania
ruff check                   # Lint
pyright aitracker_gui        # Typy (uwaga: konfiguracja w pyproject.toml wskazuje na bieżący katalog)
uv run pytest -m "not manual and not gpu and not benchmark" --cov -v   # Testy z pokryciem
```

### 6.6 Reguły ruff — szczegóły

**Włączone grupy reguł:**

| Kod | Grupa | Opis |
|-----|-------|------|
| `E` | pycodestyle | Błędy stylu PEP 8 |
| `F` | Pyflakes | Importy, zmienne nieużywane |
| `B` | flake8-bugbear | Typowe błędy logiczne |
| `Q` | flake8-quotes | Spójność cudzysłowów |
| `I` | isort | Sortowanie importów |
| `N` | pep8-naming | Konwencje nazewnictwa |
| `LOG` | flake8-logging | Poprawność logowania |
| `UP` / `UP045` | pyupgrade | Modernizacja składni Python |
| `RET` | flake8-return | Upraszczanie instrukcji return |
| `C4` | flake8-comprehensions | Optymalizacja comprehensions |
| `ISC` | flake8-implicit-str-concat | Niejawna konkatenacja stringów |
| `PIE` | flake8-pie | Zbędne instrukcje |
| `RSE` | flake8-raise | Poprawność instrukcji raise |
| `SLOT` | flake8-slots | Optymalizacja __slots__ |
| `FAST` | FastAPI | Reguły FastAPI |
| `SIM` | flake8-simplify | Uproszczenia kodu |
| `DOC` | pydoclint | Poprawność docstringów |

**Ignorowane reguły:** `E501` (długość linii — kontrolowana przez formatter), `N802`/`N815` (nazewnictwo — projekt używa CamelCase), `N999` (nazwy klas), `LOG015` (logging format).

### 6.7 Pokrycie kodu

- Narzędzie: `pytest-cov` + `coverage`
- Próg pokrycia: nie zdefiniowany jawnie w konfiguracji
- Uruchamianie: `uv run pytest --cov -v`