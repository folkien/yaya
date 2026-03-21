# YAYA — Specyfikacja Techniczna

> **YAYA — Yet Another YOLO Annoter**
> Desktopowa aplikacja Python 3.11+ / PyQt5 do tworzenia, edycji i walidacji adnotacji bounding-box w formacie YOLO.

---

## Spis treści

- [YAYA — Specyfikacja Techniczna](#yaya--specyfikacja-techniczna)
  - [Spis treści](#spis-treści)
  - [1. Architektura systemu](#1-architektura-systemu)
    - [1.1 Cel projektu](#11-cel-projektu)
    - [1.2 Diagram warstw](#12-diagram-warstw)
    - [1.3 Podział odpowiedzialności](#13-podział-odpowiedzialności)
    - [1.4 Separacja warstw](#14-separacja-warstw)
    - [1.5 Stos technologiczny](#15-stos-technologiczny)
  - [2. Konfiguracja i artefakty](#2-konfiguracja-i-artefakty)
    - [2.1 Zależności projektu](#21-zależności-projektu)
    - [2.2 Konfiguracja TOML](#22-konfiguracja-toml)
    - [2.3 Ustawienia użytkownika (QSettings)](#23-ustawienia-użytkownika-qsettings)
    - [2.4 Artefakty runtime](#24-artefakty-runtime)
    - [2.5 Modele detektorów](#25-modele-detektorów)
    - [2.6 Sesje](#26-sesje)
  - [3. Modele danych](#3-modele-danych)
    - [3.1 Typowanie](#31-typowanie)
    - [3.1a Strategia modelowania danych — dataclass vs Pydantic](#31a-strategia-modelowania-danych--dataclass-vs-pydantic)
    - [3.2 Annote — adnotacja bounding-box](#32-annote--adnotacja-bounding-box)
    - [3.3 Enumy domenowe](#33-enumy-domenowe)
    - [3.4 Metrics — metryki ewaluacji](#34-metrics--metryki-ewaluacji)
    - [3.5 Visuals — właściwości wizualne obrazu](#35-visuals--właściwości-wizualne-obrazu)
    - [3.6 AnnotationsClassifiedBool — klasyfikacja zewnętrzna](#36-annotationsclassifiedbool--klasyfikacja-zewnętrzna)
    - [3.7 Detection — surowa detekcja YOLO](#37-detection--surowa-detekcja-yolo)
    - [3.8 Dataset — zbiór ścieżek plików](#38-dataset--zbiór-ścieżek-plików)
    - [3.9 Session — sesja programu](#39-session--sesja-programu)
    - [3.10 BoxState — stan okluzji](#310-boxstate--stan-okluzji)
    - [3.11 fileEntry — słownik danych pliku](#311-fileentry--słownik-danych-pliku)
    - [3.12 Formaty bounding-boxów](#312-formaty-bounding-boxów)
  - [4. Moduły i logika biznesowa](#4-moduły-i-logika-biznesowa)
    - [4.1 engine/ — rdzeń aplikacji](#41-engine--rdzeń-aplikacji)
      - [Annoter — główny silnik adnotacji](#annoter--główny-silnik-adnotacji)
      - [dataset.py — zarządzanie zbiorami danych](#datasetpy--zarządzanie-zbiorami-danych)
      - [GuiClassKeycodes — mapowanie klawiszy](#guiclasskeycodes--mapowanie-klawiszy)
      - [annotators/ — strategie wizualizacji (Strategy)](#annotators--strategie-wizualizacji-strategy)
    - [4.2 Detectors/ — warstwa detekcji](#42-detectors--warstwa-detekcji)
      - [Fabryka detektorów](#fabryka-detektorów)
      - [Klasa bazowa Detector](#klasa-bazowa-detector)
      - [Implementacje detektorów](#implementacje-detektorów)
    - [4.3 helpers/ — biblioteka narzędzi](#43-helpers--biblioteka-narzędzi)
      - [Bounding-boxy i NMS](#bounding-boxy-i-nms)
      - [Pliki i adnotacje](#pliki-i-adnotacje)
      - [Analiza obrazów](#analiza-obrazów)
      - [Metryki i algebra](#metryki-i-algebra)
      - [Infrastruktura](#infrastruktura)
    - [4.4 Warstwa prezentacji (GUI)](#44-warstwa-prezentacji-gui)
      - [Internacjonalizacja (i18n)](#internacjonalizacja-i18n)
      - [MainWindowGui — kontroler głównego okna](#mainwindowgui--kontroler-głównego-okna)
      - [ViewerEditorImage — interaktywny edytor obrazu](#viewereditorimage--interaktywny-edytor-obrazu)
      - [Widoki tabel (views/)](#widoki-tabel-views)
      - [Widgety tabelowe (Gui/widgets/)](#widgety-tabelowe-guiwidgets)
    - [4.5 Decorators/ — analiza datasetu](#45-decorators--analiza-datasetu)
    - [4.6 models/ — integracje zewnętrzne](#46-models--integracje-zewnętrzne)
  - [5. Przepływ sterowania](#5-przepływ-sterowania)
    - [5.1 Sekwencja startu](#51-sekwencja-startu)
    - [5.2 Otwieranie lokalizacji](#52-otwieranie-lokalizacji)
    - [5.3 Przetwarzanie bieżącego pliku](#53-przetwarzanie-bieżącego-pliku)
    - [5.4 Ewaluacja metryk](#54-ewaluacja-metryk)
    - [5.5 Non-Maximum Suppression](#55-non-maximum-suppression)
    - [5.6 Logowanie](#56-logowanie)
    - [5.7 Obsługa warunków brzegowych](#57-obsługa-warunków-brzegowych)
  - [6. Testowanie i jakość kodu](#6-testowanie-i-jakość-kodu)
    - [6.1 Framework testowy](#61-framework-testowy)
    - [6.2 Markery testów](#62-markery-testów)
    - [6.3 Pliki testowe](#63-pliki-testowe)
    - [6.4 Mockowanie](#64-mockowanie)
    - [6.5 Analiza statyczna i lint](#65-analiza-statyczna-i-lint)
      - [Zasady organizacji importów](#zasady-organizacji-importów)

---

## 1. Architektura systemu

### 1.1 Cel projektu

YAYA jest narzędziem dla inżynierów danych i badaczy Computer Vision. Realizuje:

- **Ręczne adnotowanie** — rysowanie, edycja i usuwanie bounding-boxów na obrazach.
- **Automatyczna detekcja** — integracja z backendami YOLO (YOLOv4 Darknet, YOLOv5/v8/v11 Ultralytics, YOLO World).
- **Walidacja adnotacji** — porównanie detekcji z adnotacjami ręcznymi (TP/FP/FN, Precision, Recall).
- **Analiza wizualna datasetu** — HSV, rozmiary obiektów, duplikaty (image hashing), rozkład klas.
- **Zarządzanie datasetem** — filtrowanie, podział treningowy/walidacyjny, eksport.

### 1.2 Diagram warstw

Monolityczna aplikacja desktopowa — pojedynczy proces.

```
┌──────────────────────────────────────────────────┐
│  yolo-annotate.py  (entry-point, argparse, boot) │
└────────┬────────────────────┬────────────────────┘
         │                    │
   ┌─────▼──────┐    ┌───────▼────────┐
   │ MainWindow │◄──►│    Annoter     │
   │   (GUI)    │    │ (engine core)  │
   └─────┬──────┘    └───────┬────────┘
         │                   │
   ┌─────▼──────┐    ┌───────▼────────┐
   │   Views    │    │   Detectors    │
   │  (tabele)  │    │(YOLO backends) │
   └─────┬──────┘    └───────┬────────┘
         │                   │
   ┌─────▼───────────────────▼─────────┐
   │            helpers/               │
   │  (boxes, metrics, files, visuals) │
   └───────────────────────────────────┘
```

> **Konteneryzacja — perspektywa rozwoju:** Warstwa GUI (PyQt5) z natury wymaga bezpośredniego dostępu do systemu okienkowego i nie podlega konteneryzacji. Natomiast warstwa detekcji (`Detectors/`) jest bezstanowa i intensywna obliczeniowo — stanowi naturalnego kandydata do wydzielenia jako kontenerowy worker (Docker + NVIDIA Container Toolkit). Potencjalny model: GUI komunikuje się z workerami detekcji przez kolejkę zadań (np. ZeroMQ, Redis) lub gRPC — bez wystawiania portów zewnętrznych. Taka architektura umożliwiłaby: (a) izolację zależności GPU, (b) skalowanie horyzontalne detekcji, (c) uruchamianie workerów na zdalnych maszynach. **Decyzja:** aktualnie projekt pozostaje monolitem; refaktoryzacja do modelu worker opisana jest jako przyszły kierunek, gdy skala przetwarzania tego wymusi.

### 1.3 Podział odpowiedzialności

| Warstwa | Katalogi | Odpowiedzialność |
|---------|----------|------------------|
| Entry-point | `yolo-annotate.py` | Parsowanie CLI, bootstrap detektora/annotera, uruchomienie GUI |
| Kontroler GUI | `MainWindow.py`, `ViewerEditorImage.py` | Główne okno, interaktywny edytor bounding-boxów |
| Widoki | `views/` | Generowanie zawartości `QTableWidget` (prezentacja danych) |
| Silnik | `engine/` | Logika domenowa — adnotacje, pliki, metryki, konfiguracja. **Bez** zależności od PyQt5 |
| Detektory | `Detectors/` | Abstrakcja nad backendami YOLO (Darknet, OpenCV DNN, Ultralytics) |
| Helpery | `helpers/` | Bounding-boxy, NMS, pliki, metryki, rysowanie, kolory |
| Widgety | `Gui/` | Niestandardowe `QTableWidgetItem`, stałe kolorów |
| Dekoratory | `Decorators/` | Generatory raportów i wizualizacji datasetu |
| Modele | `models/` | Struktury danych dla integracji zewnętrznych |

### 1.4 Separacja warstw

Zasada architektoniczna: **`engine/` nie zależy od PyQt5**. Warstwa prezentacji deleguje operacje domenowe do silnika.

Wyjątek: `engine/annotators/` — kod rysowania adnotacji na `QPainter` (wzorzec Strategy). Logika decyzyjna (ocena TP/FP/FN) pozostaje w silniku.

### 1.5 Stos technologiczny

| Komponent | Technologia |
|-----------|-------------|
| Język | Python 3.11+ |
| GUI | PyQt5 5.15.7 |
| Computer Vision | OpenCV (headless) 4.7, NumPy <2.0 |
| Detekcja | Ultralytics ≥8.3, opcjonalnie Darknet (ctypes) |
| Analiza danych | pandas, imagehash |
| Build system | pdm-backend |
| Menedżer pakietów | `uv` |

---

## 2. Konfiguracja i artefakty

### 2.1 Zależności projektu

Definiowane w `pyproject.toml`.

**Runtime:**

| Pakiet | Wersja | Rola |
|--------|--------|------|
| `pyqt5` | 5.15.7 | Framework GUI |
| `opencv-python-headless` | 4.7.0.72 | Przetwarzanie obrazów, backend DNN |
| `numpy` | <2.0.0 | Operacje na tablicach |
| `pandas` | ≥2.2.3 | Analiza danych, DataFrame |
| `ultralytics` | ≥8.3.191 | Detektor YOLOv5/v8/v11 |
| `imagehash` | 4.3.1 | Perceptualny hashing obrazów |
| `tqdm` | ≥4.67.1 | Paski postępu |

**Deweloperskie:**

| Narzędzie | Rola |
|-----------|------|
| `ruff` | Formatowanie + lint |
| `pyright` | Statyczna analiza typów (`strict`) |
| `pytest` + `pytest-cov` | Testy + pokrycie kodu |
| `pyqt5-stubs` | Type stubs dla PyQt5 |
| `isort` | Sortowanie importów |
| `taplo` | Formatowanie TOML |

**Konfiguracja narzędzi:**

- **Pyright:** `typeCheckingMode = "strict"`
- **Ruff:** `line-length = 120`, preview mode, reguły: E, F, B, Q, I, N, LOG, UP, RET, C4, ISC, PIE, RSE, SLOT, FAST, SIM, DOC
- **Build:** `pdm-backend`

### 2.2 Konfiguracja TOML

System oparty na plikach TOML z mechanizmem fallback: `config.toml` → `config.example.toml`.

Klasa `ConfigToml` (`engine/config_toml.py`) — Singleton. Łańcuch ładowania:

1. Próba odczytu `config.toml`.
2. Fallback do `config.example.toml`.
3. Brak obu → `FileNotFoundError`.
4. Nieprawidłowy TOML → `sys.exit`.

**API:**

| Metoda | Zachowanie |
|--------|------------|
| `get(key, default)` | Bezpieczne pobranie z fallbackiem |
| `__getitem__(key)` | Pobranie lub `sys.exit` z komunikatem |

**Schemat konfiguracji:**

```toml
[detector]
detector = "Default"           # Default | YoloWorld
confidence = 0.25              # Próg confidence
nms = 0.45                     # Próg NMS
nms_method = "greedy"          # Nms | SoftNms | NmWeighted | WeightedBoxFusion
image_strategy = "resize"      # Rescale | LetterBox | Tiling2x2 | Tiling

[detector.ultralytics]
force_cpu = false
task = "detect"                # detect | segment | classify
half_precision = true          # FP16 inference
use_tensorrt = false

[detector.yolo_world]
default_prompt = "warning lamp:lamp1, emergency light:lamp2"
```

### 2.3 Ustawienia użytkownika (QSettings)

Dane sesji przechowywane w systemowym rejestrze Qt:

- Historia otwartych katalogów — stack do 64 pozycji.
- Organizacja: `AISP` / `aisp.pl` / `YAYA`.

### 2.4 Artefakty runtime

Pliki generowane w katalogu obrazów:

| Rozszerzenie | Opis |
|--------------|------|
| `.txt` | Adnotacje YOLO (`classNumber x y w h`) |
| `.detector` | Cache detekcji (`className confidence x y w h`) |
| `.yoloworld` | Cache detekcji YOLO World |
| `.visuals.json` | Dane wizualne (HSV grid, dhash, wymiary) |
| `dataset.txt` | Lista annotowanych plików |
| `validation.txt` | Lista plików walidacyjnych |

### 2.5 Modele detektorów

Wagi modeli (pliki `.weights`, `.pt`) są artefaktami binarnymi o rozmiarze rzędu setek MB. **Muszą** być zarządzane przez **Git LFS**, aby repozytorium pozostało responsywne. Pliki metadanych (`.cfg`, `.data`, `.names`) są zwykłymi plikami tekstowymi i mogą być wersjonowane standardowo.

**Konfiguracja Git LFS** (jednorazowa inicjalizacja):

```bash
git lfs install
git lfs track "Detectors/**/*.weights"
git lfs track "Detectors/**/*.pt"
# Reguły zapisywane w .gitattributes (wersjonowany)
```

**Struktura katalogu modelu:**

```
Detectors/<nazwa_modelu>/
├── model.cfg / model.pt      # Wagi sieci (Git LFS)
├── model.weights              # Wagi Darknet (Git LFS)
├── model.data                 # Metadane (Darknet)
└── model.names                # Nazwy klas
```

> **Uwaga:** Po migracji z ręcznego umieszczania plików na Git LFS należy wykonać `git lfs migrate import` na istniejących plikach binarnych, a następnie wymusić `git push --force` na dotkniętych branchach.

Fabryka `ListDetectors()` skanuje podkatalogi i wykrywa modele na podstawie rozszerzeń (`.cfg`+`.weights`+`.names` lub `.pt`+`.names`).

### 2.6 Sesje

Dataclass `Session` tworzy snapshoty do `temp/session_YYYYMMDD_HHMM/`. Kopiowane artefakty: obraz, `.txt`, `.detector`, `.visuals`.

---

## 3. Modele danych

### 3.1 Typowanie

Projekt stosuje Pyright w trybie `strict`. Zasady:

- Wszystkie funkcje/metody posiadają pełne adnotacje typów (argumenty + wartość zwracana).
- Składnia Python 3.10+: `list[str]`, `str | None` (nie `List[str]`, `Optional[str]`).
- `TYPE_CHECKING` jest **zabroniony** — import musi być bezwarunkowy i dostępny w runtime.
- Tablice NumPy: alias `NumpyArray` z `helpers.aisp_typing`.

### 3.1a Strategia modelowania danych — dataclass vs Pydantic

Obecnie modele danych (`Metrics`, `Visuals`, `Session`, `Detection`, `Annote`) są zaimplementowane jako `@dataclass`. Dla nowych, złożonych modeli danych — szczególnie tych przyjmujących dane z zewnątrz (pliki, API, konfiguracja użytkownika) — **zaleca się** stosowanie **Pydantic `BaseModel`**, co zapewnia:

- **Automatyczną walidację typów** w runtime (nie tylko statycznie przez Pyright).
- **Koercję typów** — np. `"42"` → `42` przy odczycie z pliku.
- **Czytelną serializację** — `model_dump()`, `model_dump_json()` zamiast ręcznej konwersji `dataclasses.asdict()`.
- **Metadane pól** — `Field(alias=..., json_schema_extra=...)` dla selektywnej serializacji (np. CSV vs baza).

**Reguła migracji:** istniejące `@dataclass` nie muszą być migrowane na Pydantic, chyba że:
1. Model przyjmuje dane z niezaufanego źródła (plik użytkownika, API, CSV).
2. Wymagana jest walidacja danych wykraczająca poza proste typowanie.
3. Model wymaga złożonej serializacji/deserializacji (aliasy, wykluczenia pól).

Zasady Pydantic — patrz `copilot-instructions.md`, sekcja „Pydantic BaseModel".

### 3.2 Annote — adnotacja bounding-box

Centralna encja systemu. Lokalizacja: `engine/annote.py`.

**Pola:**

| Pole | Typ | Opis |
|------|-----|------|
| `box` | `tuple[float, float, float, float]` | Bbox znormalizowany (x1, y1, x2, y2), format xyxy, zakres 0–1 |
| `classNumber` | `int` | Numer klasy |
| `className` | `str` | Nazwa klasy |
| `confidence` | `float` | Pewność detekcji (0–100) |
| `authorType` | `AnnoteAuthorType` | Źródło adnotacji |
| `evalution` | `AnnoteEvaluation` | Wynik ewaluacji |
| `evaluation_iou` | `float` | IOU z najlepszym dopasowaniem |
| `evaluation_confidence` | `float` | Confidence dopasowanej detekcji |
| `evaluation_class_id` | `int` | ID klasy z ewaluacji (−1 = brak) |
| `hue` | `float` | Wartość H (HSV) wycinka obrazu |
| `saturation` | `float` | Wartość S (HSV) |
| `brightness` | `float` | Wartość V (HSV) |

**Properties obliczeniowe:**

| Property | Typ | Opis |
|----------|-----|------|
| `width` | `float` | Szerokość bbox (znormalizowana) |
| `height` | `float` | Wysokość bbox (znormalizowana) |
| `area` | `float` | Powierzchnia bbox |
| `ratio` | `float` | Stosunek szerokości do wysokości |
| `class_abbrev` | `str` | Skrót nazwy klasy (max 3 znaki, uppercase) |
| `evaluation_class_name` | `str` | Nazwa klasy z ewaluacji |

**Serializacja:**

| Funkcja | Kierunek | Opis |
|---------|----------|------|
| `toTxtAnnote(annote)` | Annote → tuple | Format pliku `.txt` (classNumber, box) |
| `fromTxtAnnote(txt)` | tuple → Annote | Tworzenie z rekordu `.txt` |
| `toYoloDetection(annote)` | Annote → tuple | Format (className, 100, box) |
| `fromDetection(detection)` | tuple → Annote | Tworzenie z detekcji |

**Globalna lista klas:** przechowywana w module `annote.py`, inicjalizowana przez `Init(names)`. Dostęp: `GetClasses()`, `GetClassName(number)`, `GetClassNumber(name)`.

### 3.3 Enumy domenowe

Lokalizacja: `engine/annote_enums.py`.

**`AnnoteAuthorType`** — źródło adnotacji:

| Wartość | Opis |
|---------|------|
| `byHuman` (0) | Wczytana z pliku `.txt` |
| `byDetector` (1) | Wygenerowana przez detektor |
| `byHand` (2) | Narysowana ręcznie w bieżącej sesji |

**`AnnoteEvaluation`** — wynik ewaluacji:

| Wartość | Opis |
|---------|------|
| `noEvaluation` (0) | Brak ewaluacji |
| `TruePositiveLabel` (1) | Bbox + klasa dopasowane |
| `TruePositive` (2) | Bbox dopasowany, klasa inna |
| `FalseNegative` (3) | Adnotacja bez dopasowanej detekcji |

**`AnnotatorType`** — strategia wizualizacji:

| Wartość | Logika kolorowania |
|---------|-------------------|
| `Default` | Kolor zależy od `authorType`/`evaluation` |
| `ConfidenceHeat` | Mapa cieplna wg confidence |
| `Category` | Kolor wg numeru klasy (paleta matplotlib) |

### 3.4 Metrics — metryki ewaluacji

Lokalizacja: `helpers/metrics.py`. Dataclass.

| Pole | Typ | Domyślna | Opis |
|------|-----|----------|------|
| `All` | `int` | 0 | Liczba adnotacji |
| `AvgWidth` | `float` | −1.0 | Średnia szerokość adnotacji |
| `AvgHeight` | `float` | −1.0 | Średnia wysokość adnotacji |
| `iou_avg` | `float` | 0.0 | Średnie najlepsze IOU |
| `overlapping_iou` | `float` | 0.0 | IOU nakładania się adnotacji |
| `TP` | `int` | 0 | True Positives (bbox dopasowany) |
| `FP` | `int` | 0 | False Positives (detekcja bez adnotacji) |
| `TN` | `int` | 0 | True Negatives (nieużywane) |
| `FN` | `int` | 0 | False Negatives (adnotacja bez detekcji) |
| `LTP` | `int` | 0 | Label True Positives (bbox + klasa) |
| `detections` | `list` | `[]` | Wszystkie detekcje |
| `new_detections` | `list` | `[]` | Niedopasowane detekcje |
| `matches` | `list` | `[]` | Pary (annotation, detection) |

Properties obliczeniowe: `correct`, `correct_bboxes`, `precision`, `recall`, `mAP`, `AvgSize`, `detections_confidence`, `detections_confidence_min`, `matches_confidence`.

Listy mutowalne korzystają z `default_factory=list`.

### 3.5 Visuals — właściwości wizualne obrazu

Lokalizacja: `helpers/visuals.py`. Dataclass.

| Pole | Typ | Opis |
|------|-----|------|
| `imagepath` | `str` | Ścieżka do obrazu |
| `width` | `float` | Szerokość obrazu |
| `height` | `float` | Wysokość obrazu |
| `grid` | `list[tuple[float, float, float]]` | Siatka 20×20 wartości HSV |
| `dhash` | `str` | Perceptualny hash (imagehash) |
| `isDuplicate` | `bool` | Flaga duplikatu |

Wzorzec fabrykujący: `Visuals.LoadCreate(imagepath, force)` — ładuje z cache JSON lub tworzy nowy obiekt i zapisuje.

Serializacja: `dataclasses.asdict()` → JSON (`helpers.json.jsonWrite/jsonRead`).

### 3.6 AnnotationsClassifiedBool — klasyfikacja zewnętrzna

Lokalizacja: `models/annotations_classified.py`. Dataclass.

Przechowuje wyniki binarnej klasyfikacji adnotacji (np. GPT). Pola jako tablice NumPy:

| Pole | Typ NumPy | Opis |
|------|-----------|------|
| `filenames` | `NDArray[np.str_]` | Nazwy plików |
| `class_ids` | `NDArray[np.int16]` | ID klas |
| `x`, `y`, `w`, `h` | `NDArray[np.float32]` | Współrzędne bbox |
| `bools` | `NDArray[np.bool_]` | Wynik klasyfikacji True/False |

Serializacja: `from_csv()` via pandas → NumPy; `to_csv()` via DataFrame → CSV.

### 3.7 Detection — surowa detekcja YOLO

Lokalizacja: `Detectors/common/Detection.py`. Dataclass.

| Pole | Typ | Opis |
|------|-----|------|
| `xywh` | `list[float]` | Bbox center (x, y, w, h) |
| `objectness` | `float` | Wartość objectness z YOLO HEAD |
| `probabilities` | `list[float]` | Prawdopodobieństwa per klasa |

Properties: `confidence` (max z probabilities), `class_id` (argmax), `class_label` (nazwa klasy).

### 3.8 Dataset — zbiór ścieżek plików

Lokalizacja: `engine/dataset.py`.

| Pole | Typ | Opis |
|------|-----|------|
| `_path` | `str \| None` | Ścieżka do pliku dataset |
| `_dataset` | `set[str]` | Zbiór nazw plików |
| `_is_not_saved` | `bool` | Flaga niezapisanych zmian |

Metody: `add(path)`, `remove(path)`, `load(path)`, `save()`, `is_inside(path)`.

### 3.9 Session — sesja programu

Lokalizacja: `engine/session.py`. Dataclass.

| Pole | Typ | Opis |
|------|-----|------|
| `timestamp` | `datetime` | Czas startu (`default_factory=datetime.now`) |

Property: `session_path` → `temp/session_YYYYMMDD_HHMM/`.

### 3.10 BoxState — stan okluzji

Lokalizacja: `helpers/boxes.py`. Bitmaskowy enum.

| Bit | Stała | Opis |
|-----|-------|------|
| 0x00 | `Isolated` | Box izolowany |
| 0x01 | `Occluding` | Box zasłaniający inny |
| 0x02 | `Occluded` | Box zasłonięty |
| 0x04 | `Containing` | Box zawierający inny |
| 0x08 | `Contained` | Box zawarty w innym |

### 3.11 fileEntry — słownik danych pliku

Struktura `dict` generowana w `Annoter.OpenLocation()`, przepływająca przez cały system.

| Klucz | Typ | Opis |
|-------|-----|------|
| `Name` | `str` | Nazwa pliku obrazu |
| `Path` | `str` | Pełna ścieżka |
| `ID` | `int` | Indeks w liście plików |
| `IsAnnotation` | `bool` | Istnienie pliku `.txt` |
| `IsValidation` | `bool` | Przynależność do zbioru walidacyjnego |
| `Annotations` | `list[Annote]` | Adnotacje ludzkie |
| `AnnotationsClasses` | `str` | Skróty klas (CSV) |
| `Datetime` | `float` | Timestamp modyfikacji pliku |
| `Errors` | `int` | Liczba błędów |
| `Detections` | `list[Annote]` | Detekcje (po filtracji IOU) |
| `Detections_original` | `list[Annote]` | Detekcje oryginalne |
| `Metrics` | `Metrics` | Metryki ewaluacji |
| `Visuals` | `Visuals` | Dane wizualne |

### 3.12 Formaty bounding-boxów

| Format | Struktura | Zakres | Zastosowanie |
|--------|-----------|--------|--------------|
| YOLO (xywh) | `(center_x, center_y, w, h)` | 0–1 | Pliki `.txt`, detekcje |
| Rect (xyxy) | `(x1, y1, x2, y2)` | 0–1 | Wewnętrzna repr. w `Annote.box` |
| Absolute (xyxy px) | `(x1, y1, x2, y2)` | piksele | Rysowanie na obrazie |

Konwersje (`helpers/boxes.py`): `Bbox2Rect()` / `Rect2Bbox()` — YOLO ↔ xyxy; `ToAbsolute()` / `ToRelative()` — znormalizowane ↔ piksele; `to_xyxy()` — alias YOLO → xyxy.

---

## 4. Moduły i logika biznesowa

### 4.1 engine/ — rdzeń aplikacji

#### Annoter — główny silnik adnotacji

Lokalizacja: `engine/annoter.py`. Centralny komponent logiki biznesowej. Niezależny od PyQt5.

**Odpowiedzialności:**

- Skanowanie katalogu z obrazami, sortowanie, nawigacja, filtrowanie.
- Integracja z detektorami YOLO (uruchamianie, cache wyników).
- Ładowanie/zapis adnotacji i detekcji (`.txt`, `.detector`).
- Ewaluacja metryk TP/FP/FN/Precision/Recall.
- Cache właściwości wizualnych (HSV, dhash).
- Wykrywanie duplikatów obrazów.
- Zarządzanie datasetem treningowym/walidacyjnym.

**Wejście:** `filepath` (katalog z obrazami), `detector` (instancja detektora lub `None`), parametry konfiguracyjne (`detectorConfidence`, `detectorNms`, flagi filtrów).

**Wyjście:** `self.files` (lista `fileEntry`), `self.annotations` (adnotacje bieżącego pliku), `self.image` (bieżący obraz cv2).

**Sortowanie:**

| Stała | Opis |
|-------|------|
| `NoSort` | Bez sortowania |
| `SortByDatetime` | Chronologicznie rosnąco |
| `SortByInvDatetime` | Chronologicznie malejąco (domyślne) |
| `SortByAlphabet` | Alfabetycznie |

**Filtry (stosowane w `OpenLocation`):**

| Flaga | Efekt |
|-------|-------|
| `isOnlyNewFiles` | Pliki bez adnotacji |
| `isOnlyOldFiles` | Pliki z adnotacjami |
| `isOnlyErrorFiles` | Pliki z błędami |
| `isOnlySpecificClass` | Pliki z konkretną klasą |

**Kluczowe metody:**

| Metoda | Opis |
|--------|------|
| `OpenLocation(path)` | Skanowanie katalogu, załadowanie danych per plik |
| `Process()` | Przetworzenie bieżącego pliku (obraz, adnotacje, detekcje, metryki) |
| `ProcessNext()` / `ProcessPrev()` | Nawigacja i przetwarzanie sąsiedniego pliku |
| `Save()` | Zapis adnotacji do `.txt` |
| `AddAnnotation(box, classNumber)` | Dodanie adnotacji |
| `RemoveAnnotation(element)` | Usunięcie adnotacji |
| `Delete()` | Usunięcie pliku obrazu i adnotacji |
| `ProcessDetections(im, filepath)` | Uruchomienie detekcji |
| `CalculateYoloMetrics(annotations, detections)` | Obliczenie metryk |
| `GetFiles(filter_*_classnames)` | Pobranie plików z filtrowaniem po klasach |

#### dataset.py — zarządzanie zbiorami danych

Zarządza plikami `dataset.txt` i `validation.txt`.

| Metoda | Opis |
|--------|------|
| `add(path)` | Dodaje ścieżkę (guard clause na duplikat) |
| `remove(path)` | Usuwa ścieżkę (guard clause na brak) |
| `load(path)` | Wczytuje plik, waliduje istnienie, auto-usuwa nieistniejące |
| `save()` | Zapisuje posortowane ścieżki |
| `is_inside(path)` | Sprawdza przynależność |

#### GuiClassKeycodes — mapowanie klawiszy

Mapuje klawisze `1`–`0`, `-`, `=`, `` ` `` na numery klas. Klawisz `` ` `` pełni rolę modyfikatora offsetu (+12 klas), obsługa >12 klas.

#### annotators/ — strategie wizualizacji (Strategy)

Dispatcher `Annotator.QtDraw()` deleguje rysowanie do strategii na podstawie `AnnotatorType`.

| Strategia | Klasa | Logika kolorowania |
|-----------|-------|-------------------|
| Default | `AnnotatorDefault` | Wg `authorType`/`evaluation` (czarny/żółty/czerwony/zielony) |
| ConfidenceHeat | `AnnotatorConfidenceHeat` | Wg wartości confidence |
| Category | `AnnotatorCategory` | Wg numeru klasy (paleta matplotlib) |

### 4.2 Detectors/ — warstwa detekcji

#### Fabryka detektorów

Lokalizacja: `Detectors/__init__.py`.

| Funkcja | Opis |
|---------|------|
| `ListDetectors(path)` | Skanuje podkatalogi po `.cfg`+`.weights`+`.names` lub `.pt`+`.names` |
| `CreateDetector(detectorID, gpuID)` | Tworzy instancję detektora |
| `GetDetectorLabels(detectorID)` | Zwraca nazwy klas bez inicjalizacji |
| `IsDarknet()` | Sprawdza obecność `libdarknet.so` |

**`DetectorType`:**

| Wartość | Backend |
|---------|---------|
| `Darknet` | Natywna biblioteka Darknet (ctypes) |
| `CVDNN` | OpenCV DNN |
| `Ultralytics` | Ultralytics SDK (YOLOv5/v8/v11) |

#### Klasa bazowa Detector

Lokalizacja: `Detectors/common/Detector.py`.

| Metoda | Opis |
|--------|------|
| `Init()` | Inicjalizacja |
| `Detect(frame, confidence, nms_thresh, ...)` | Detekcja → `list[(label, confidence, box)]` |
| `Close()` | Zwolnienie zasobów |
| `EnsembleBoxes(boxes, scores, classids, ...)` | Filtrowanie NMS (statyczna) |
| `ToDetections(boxes, scores, classids)` | Konwersja surowych danych na listę krotek |
| `GetClassNames()` | Lista nazw klas |
| `Draw(image, detections)` | Rysowanie na obrazie (OpenCV) |

**`NmsMethod`:**

| Wartość | Algorytm | Moduł źródłowy |
|---------|----------|----------------|
| `Nms` | Klasyczny NMS | `ensemble_boxes_nms.py` |
| `SoftNms` | Soft-NMS (wygładzanie confidence) | `ensemble_boxes_nms.py` |
| `NmWeighted` | Non-Maximum Weighted (uśrednianie bbox) | `ensemble_boxes_nmw.py` |
| `WeightedBoxFusion` | Weighted Boxes Fusion (ensemble) | `ensemble_boxes_wbf.py` |

#### Implementacje detektorów

| Klasa | Backend | Wymagania |
|-------|---------|-----------|
| `DetectorYOLOv4` | `libdarknet.so` (ctypes) | Kompilacja natywnego Darknet |
| `DetectorCVDNN` | `cv2.dnn.readNetFromDarknet()` | Czysty OpenCV |
| `DetectorYolov8` | Ultralytics SDK | `pip install ultralytics` |

**`ImageStrategy`** — przetwarzanie obrazu wejściowego:

| Wartość | Opis |
|---------|------|
| `Rescale` | Przeskalowanie do rozmiaru sieci |
| `RescaleNearest` | Nearest-neighbor |
| `LetterBox` | Zachowanie proporcji + padding |
| `Tiling2x2` | Podział na 4 kafelki 2×2 |
| `Tiling` | SAHI — adaptacyjny podział |

### 4.3 helpers/ — biblioteka narzędzi

#### Bounding-boxy i NMS

| Moduł | Opis |
|-------|------|
| `boxes.py` | Konwersje formatów, IOU, geometria, okluzje |
| `ensemble_boxes_nms.py` | Klasyczny NMS + Soft-NMS |
| `ensemble_boxes_nmw.py` | Non-Maximum Weighted |
| `ensemble_boxes_wbf.py` | Weighted Boxes Fusion |
| `soft_nms.py` | Alternatywna implementacja Soft-NMS |
| `prefilters.py` | Filtr pre-NMS (IOU + confidence) |
| `detections.py` | Scalanie detekcji z kafelków |

#### Pliki i adnotacje

| Moduł | Opis |
|-------|------|
| `files.py` | Ścieżki, rozszerzenia, tworzenie katalogów, SHA-1 |
| `textAnnotations.py` | Odczyt/zapis `.txt` i `.detector` w formacie YOLO |
| `json.py` | JSON z obsługą dataclass/datetime |
| `hashing.py` | SHA-1 nazw plików |

#### Analiza obrazów

| Moduł | Opis |
|-------|------|
| `visuals.py` | HSV grid 20×20, dhash, duplikaty |
| `images.py` | Skalowanie z zachowaniem proporcji |
| `colors.py` | Stałe BGR, schematy kolorów (Bright, Matplotlib), `ColorCycler` |
| `transformations.py` | Transformacje obrazu (flip, augmentacja) |

#### Metryki i algebra

| Moduł | Opis |
|-------|------|
| `metrics.py` | Ewaluacja TP/FP/FN/Precision/Recall/mAP |
| `algebra.py` | Geometria 2D (odległość euklidesowa, translacja, kąty) |

#### Infrastruktura

| Moduł | Opis |
|-------|------|
| `Singleton.py` | Metaklasa Singleton (`ConfigToml`) |
| `gpu.py` | Detekcja CUDA/GPU, info o systemie |
| `git.py` | Info z Git (tag, branch, hash) |
| `MarkdownReport.py` | Generator raportów Markdown |
| `QtDrawing.py` | Prymitywy rysowania Qt (`QPainter`): prostokąty, elipsy, tekst, krzyżyki |

### 4.4 Warstwa prezentacji (GUI)

#### Internacjonalizacja (i18n)

Wszystkie teksty widoczne dla użytkownika (etykiety, tooltipy, komunikaty) **muszą** być owinięte w funkcję tłumaczącą — **zabrania się** twardego kodowania stringów UI w kodzie źródłowym.

| Kontekst | Mechanizm | Przykład |
|----------|-----------|----------|
| Klasy dziedziczące po `QWidget`/`QDialog` | `self.tr("...")` | `button.setText(self.tr("Delete"))` |
| Klasy **nie** dziedziczące po `QWidget` (np. `MainWindowGui`) | `QtCore.QCoreApplication.translate(context, text)` | `_translate("MainWindowGui", "Save")` |
| Teksty z parametrami | `.format()` po tłumaczeniu | `self.tr("{count} items").format(count=5)` |

- Kontekstem tłumaczenia jest nazwa klasy (pierwszy argument `translate()`).
- Źródłowe teksty pisane **po angielsku**.
- Każdy nowy plik z tłumaczeniami musi być zarejestrowany w `AITrackerConfig.pro` (sekcja `SOURCES`).
- Szczegółowe zasady i przykłady — patrz `copilot-instructions.md`, sekcja „Tłumaczenia (i18n) w PyQt5".

#### MainWindowGui — kontroler głównego okna

Lokalizacja: `MainWindow.py`. Dziedziczy `Ui_MainWindow` (auto-generowany layout).

**Zarządzane komponenty:**

- `self.annoter` — instancja `Annoter`.
- `ViewerEditorImage` — widget edytora obrazu.
- Widoki tabel: `ViewImagesTable`, `ViewAnnotations`, `ViewDetections`, `ViewFilters`, `ViewImagesSummary`.
- `self.session` — snapshoty plików.
- `self.gpt_annotations_classified` — wyniki klasyfikacji GPT.
- `self.system_settings` — `QSettings` (historia katalogów).

**Kluczowe metody:**

| Metoda | Opis |
|--------|------|
| `LocationOpen(path)` | Otwiera katalog → deleguje do `Annoter.OpenLocation()` |
| `SetupCallbacks()` | Podpięcie sygnałów Qt |
| `SetupDefault()` | Ustawienia domyślne UI |
| `OpenedDirectoriesStore/Get()` | Historia katalogów (QSettings) |
| `ImageIDToRowNumber()` / `RowNumberToImageID()` | Mapowanie wierszy tabeli ↔ ID plików |
| `Run()` | `QApplication.exec()` |

#### ViewerEditorImage — interaktywny edytor obrazu

Lokalizacja: `ViewerEditorImage.py`. Widget Qt (`QWidget`).

**Tryby edycji:**

| Tryb | Stała | Opis |
|------|-------|------|
| Brak | `ModeNone` | Nawigacja / podgląd |
| Dodawanie | `ModeAddAnnotation` | Rysowanie nowego bbox (LPM) |
| Usuwanie | `ModeRemoveAnnotation` | Usuwanie adnotacji (PPM) |
| Zmiana klasy | `ModeRenameAnnotation` | Zmiana numeru klasy |
| Malowanie | `ModePaintCircle` | Malowanie kółkiem |

**Skalowanie:**

| Tryb | Opis |
|------|------|
| `ImageScalingResize` | Dopasowanie do widgetu |
| `ImageScalingResizeAspectRatio` | Zachowanie proporcji |
| `ImageScalingOriginalSize` | Rozmiar 1:1 |
| `ImageScalingDynamicZoom` | Zoom (scroll) + panning |

Transformacje wizualne: threshold, sharpen, CLAHE, kontrast.

Sygnały: `signalEditorFinished(int)` — emitowany po zakończeniu rysowania.

#### Widoki tabel (views/)

Klasy statyczne wypełniające `QTableWidget`. Wzorzec: widok przyjmuje pustą tabelę + dane → wypełnia kolumny widgetami z `Gui/widgets/`.

| Widok | Opis |
|-------|------|
| `ViewImagesTable` | Główna tabela plików (19 kolumn: miniaturka, wymiary, adnotacje, metryki, HSV, hash) |
| `ViewAnnotations` | Tabela adnotacji ludzkich (11 kolumn: crop, klasa, confidence, ewaluacja, rozmiar, HSV) |
| `ViewDetections` | Tabela detekcji (analogiczna do ViewAnnotations) |
| `ViewFilters` | Grid przycisków filtrujących po klasach |
| `ViewImagesSummary` | Podsumowanie metryczne |

#### Widgety tabelowe (Gui/widgets/)

Niestandardowe `QTableWidgetItem` z sortowaniem numerycznym i wizualnym feedbackiem:

| Widget | Opis |
|--------|------|
| `ImageTableWidgetItem` | Miniaturka + tooltip HTML, cache (deque max 100) |
| `AnnotationsTableWidgetItem` | Lista klas z liczbą wystąpień |
| `BoolTableWidgetItem` | Zielone/czerwone tło + Yes/No |
| `EvalTableWidgetItem` | Kolor tła wg ewaluacji |
| `FloatTableWidgetItem` | Konfigurowalna precyzja, sortowanie numeryczne |
| `HsvTableWidgetItem` | Kolor tła z HSV, auto-kontrast tekstu |
| `ImhashTableWidgetItem` | Duplikaty: czerwone tło + prefix `[D]` |
| `PercentTableWidgetItem` | Skala barw R→Y→G, sortowanie numeryczne |
| `RectTableWidgetItem` | Wymiary W×H, sortowanie po powierzchni |
| `StatTableWidgetItem` | Timestamp `YYYY-MM-DD HH:MM:SS`, sortowanie chronologiczne |

### 4.5 Decorators/ — analiza datasetu

`DecoratorDistributionShowcase` — generator raportu rozkładu klas:

1. Wybiera do 9 reprezentatywnych adnotacji per kategoria (filtr po medianie rozmiaru).
2. Wycina fragmenty obrazów (crop bbox) → PNG.
3. Generuje raport Markdown z mozaikami per kategoria + statystykami.

### 4.6 models/ — integracje zewnętrzne

Struktury danych dla klasyfikatorów zewnętrznych. Jedyny model: `AnnotationsClassifiedBool` (sekcja 3.6).

---

## 5. Przepływ sterowania

### 5.1 Sekwencja startu

```
yolo-annotate.py main()
  ├─ argparse: --input, --detector, --detectorConfidence,
  │            --detectorNms, --noDetector, --forceDetector, --verbose
  ├─ logging.basicConfig(DEBUG jeśli __debug__, inaczej INFO)
  ├─ ListDetectors() → skanowanie Detectors/
  │   ├─ brak detektorów → noDetector=True, annote.Init(labels)
  │   └─ znaleziono → CreateDetector() → Init() → annote.Init(classNames)
  ├─ normalizacja ścieżki: FixPath(GetFileLocation(args.input))
  ├─ [--forceDetector] → usunięcie .detector i .json
  ├─ Annoter(filepath, detector, ...) → OpenLocation()
  └─ MainWindowGui(args, detector, annoter) → gui.Run() → app.exec()
```

### 5.2 Otwieranie lokalizacji

```
Annoter.OpenLocation(path)
  ├─ walidacja ścieżki (guard clauses: None, pusta, nieistniejąca, taka sama)
  ├─ os.listdir() → filtrowanie obrazów (IsImageFile)
  ├─ Dataset.load("validation.txt")
  ├─ VisualsDuplicates() — inicjalizacja detektora duplikatów
  └─ FOR each file (tqdm):
       ├─ ReadAnnotations() → [Annote]
       ├─ [forceDetector] cv2.imread → ProcessDetections() → SaveDetections()
       │   [else] ReadDetections() z cache .detector
       ├─ EvaluateMetrics(annotations, detections)
       ├─ prefilters.filter_iou_by_confidence()
       ├─ Visuals.LoadCreate() → HSV grid + dhash
       ├─ VisualsDuplicates.IsDuplicate() & Add()
       ├─ annote.update_hsv_from_grid()
       └─ files.append(fileEntry)
```

### 5.3 Przetwarzanie bieżącego pliku

```
Annoter.Process()
  ├─ GetFileImage() → cv2.imread
  ├─ Visuals.Create() → aktualizacja danych wizualnych
  ├─ GetFileAnnotations() → ReadAnnotations() → [Annote]
  ├─ [detector] cv2.cvtColor(BGR→RGB)
  │   ├─ ProcessDetections() → Detect() + SaveDetections()
  │   ├─ CalculateYoloMetrics()
  │   └─ prefilters.filter_iou_by_confidence()
  └─ self.annotations = txtAnnotations + detAnnotes
```

### 5.4 Ewaluacja metryk

Algorytm `EvaluateMetrics(annotations, detections, minConfidence=0.5, minIOU=0.5)`:

1. Guard: brak adnotacji → `Metrics(FP=len(detections))`.
2. Guard: brak detekcji → `Metrics(All=len(annotations))`.
3. Filtr `confidence > minConfidence`.
4. Obliczenie `overlapping_iou` (nakładanie adnotacji).
5. Dla każdej adnotacji:
   - IOU z każdą detekcją → sortowanie malejąco.
   - `iou_best < minIOU` → `FalseNegative`.
   - `iou_best ≥ minIOU` + klasa zgodna → `TruePositiveLabel`.
   - `iou_best ≥ minIOU` + klasa inna → `TruePositive`.
   - Usunięcie dopasowanej detekcji z puli.

### 5.5 Non-Maximum Suppression

`Detector.EnsembleBoxes()` deleguje do algorytmu wg `NmsMethod`:

| Metoda | Funkcja | Moduł |
|--------|---------|-------|
| `Nms` | `nms()` | `ensemble_boxes_nms.py` |
| `SoftNms` | `soft_nms()` | `ensemble_boxes_nms.py` |
| `NmWeighted` | `non_maximum_weighted()` | `ensemble_boxes_nmw.py` |
| `WeightedBoxFusion` | `weighted_boxes_fusion()` | `ensemble_boxes_wbf.py` |

### 5.6 Logowanie

Standardowy moduł `logging` Pythona.

- Konfiguracja globalna: `logging.basicConfig()` w `yolo-annotate.py` (DEBUG w trybie debug, INFO w produkcji).
- Loggery per moduł: `logger = logging.getLogger(__name__)`.

**Poziomy:**

| Poziom | Zastosowanie |
|--------|--------------|
| `DEBUG` | Szczegóły operacji (dodanie/zapis adnotacji) |
| `INFO` | Istotne zdarzenia (otwarcie lokalizacji, znalezienie detektora) |
| `WARNING` | Brak detektorów, nieistniejące pliki w datasecie |
| `ERROR` | Nieistniejące ścieżki, nieprawidłowe nazwy klas |
| `FATAL` | Błędy cv2 przy odczycie obrazu, duplikaty rejestracji |

### 5.7 Obsługa warunków brzegowych

Projekt stosuje **guard clauses** (wczesne wyjścia) i **graceful degradation**:

**Graceful degradation:**

| Scenariusz | Reakcja |
|------------|---------|
| Brak detektora | `noDetector = True`, aplikacja działa bez detekcji |
| Nieistniejący plik w datasecie | Auto-usunięcie wpisu, kontynuacja |
| Błąd cv2 przy odczycie obrazu | `logging.fatal()`, zwrot `None` |
| Brak pliku konfiguracyjnego | Fallback do `config.example.toml` |
| Duplikat w zbiorze | `logging.error()` + return (bez wyjątku) |

**Walidacja adnotacji:** metoda `__checkOfErrors()` w `Annoter` sprawdza nakładanie bbox (overlapping) za pomocą `prefilters.filter_iou_by_confidence()`. Błędy gromadzone w `self.errors` (`set[str]`).

**Warunki brzegowe warstwy GUI (ViewerEditorImage):**

Komponent `ViewerEditorImage` obsługuje defensywnie nieprzewidywalne akcje użytkownika:

| Scenariusz | Reakcja |
|------------|--------|
| Rysowanie bbox całkowicie poza obszarem obrazu | Adnotacja odrzucona (walidacja współrzędnych w `mouseReleaseEvent`) — nie trafia do listy |
| Bbox o zerowej powierzchni (kliknięcie bez przeciągnięcia) | Ignorowany — guard clause na minimalny rozmiar bbox |
| Bbox wychodzący częściowo poza obraz | Przycinanie (clamp) współrzędnych do zakresu [0, 1] przed zapisem |
| Brak załadowanego obrazu (pusty widget) | Tryby edycji zablokowane — `paintEvent` rysuje wyłącznie placeholder |
| Scroll/zoom poza granice obrazu | Panning ograniczony do widocznego obszaru — zaciskanie offset do dopuszczalnego zakresu |
| Próba usunięcia adnotacji przy braku adnotacji pod kursorem | Brak akcji — `RemoveAnnotation` operuje na hit-teście, brak trafienia = brak efektu |

---

## 6. Testowanie i jakość kodu

### 6.1 Framework testowy

- **Framework:** `pytest` (bez klas `unittest`).
- **Lokalizacja:** `tests/`.
- **Uruchamianie:** `uv run pytest -m "not manual and not gpu and not benchmark" -v`.

### 6.2 Markery testów

| Marker | Opis | Uruchamiany w CI |
|--------|------|------------------|
| *(brak)* | Testy jednostkowe | Tak |
| `benchmark` | Testy wydajnościowe | Nie |
| `gpu` | Testy wymagające CUDA/GPU | Nie |
| `manual` | Testy integracyjne z zasobami zewnętrznymi | Nie |

Domyślny filtr CI: `-m "not manual and not gpu and not benchmark"`.

### 6.3 Pliki testowe

| Plik | Typ | Zakres |
|------|-----|--------|
| `test_boxes.py` | Jednostkowy | `helpers.boxes.tiles_iou()` — IOU kafelków |
| `test_benchmark_nms.py` | Benchmark | Wydajność 4 metod NMS |
| `test_gpu.py` | GPU | Dostępność CUDA (`CudaDeviceLowestMemory()`) |
| `test_yolo_world.py` | Integracyjny | YOLO World: detekcja klas tekstowych |

Dane testowe `test_yolo_world.py` w katalogu `tests/yolo_world/`.

### 6.4 Mockowanie

`MagicMock` z `unittest.mock` dla złożonych zależności. Helpery (`boxes`, `metrics`) testowane bezpośrednio — nie wymagają mocków.

### 6.5 Analiza statyczna i lint

| Narzędzie | Konfiguracja | Rola |
|-----------|-------------|------|
| Pyright | `strict` mode | Pełna statyczna analiza typów |
| Ruff format | `line-length = 120` | Formatowanie kodu |
| Ruff lint | Preview, 18 grup reguł | Kompleksowy lint |

#### Zasady organizacji importów

Importy w każdym pliku **muszą** być zorganizowane w trzech rozdzielonych pustą linią blokach, w następującej kolejności:

1. **Biblioteka standardowa** — `os`, `logging`, `datetime`, `dataclasses`, itp.
2. **Zależności zewnętrzne** — `numpy`, `cv2`, `pandas`, `PyQt5`, `ultralytics`, itp.
3. **Moduły lokalne** — `engine.*`, `helpers.*`, `Detectors.*`, `Gui.*`, `views.*`, itp.

Dodatkowe wymagania:
- **Wyłącznie importy absolutne** — zabronione są importy relatywne (`from . import`, `from .. import`). Każdy import musi jednoznacznie wskazywać pełną ścieżkę modułu.
- Sortowanie importów w obrębie bloków jest wymuszane przez regułę Ruff `I` (isort).
- Reguła `I` jest aktywna w konfiguracji Ruff — naruszenia blokują CI.

**Przykład poprawnej organizacji:**

```python
import logging
import os
from dataclasses import dataclass, field

import cv2
import numpy as np
from PyQt5.QtCore import Qt

from engine.annote import Annote, GetClassName
from helpers.boxes import Bbox2Rect, iou
```

**Reguły ruff:**

| Kod | Grupa | Opis |
|-----|-------|------|
| `E` | pycodestyle | Styl PEP 8 |
| `F` | Pyflakes | Nieużywane importy/zmienne |
| `B` | flake8-bugbear | Typowe błędy logiczne |
| `Q` | flake8-quotes | Spójność cudzysłowów |
| `I` | isort | Sortowanie importów |
| `N` | pep8-naming | Konwencje nazewnictwa |
| `LOG` | flake8-logging | Poprawność logowania |
| `UP` | pyupgrade | Modernizacja składni Python |
| `RET` | flake8-return | Upraszczanie return |
| `C4` | flake8-comprehensions | Optymalizacja comprehensions |
| `ISC` | flake8-implicit-str-concat | Niejawna konkatenacja |
| `PIE` | flake8-pie | Zbędne instrukcje |
| `RSE` | flake8-raise | Poprawność raise |
| `SLOT` | flake8-slots | Optymalizacja `__slots__` |
| `FAST` | FastAPI | Reguły FastAPI |
| `SIM` | flake8-simplify | Uproszczenia kodu |
| `DOC` | pydoclint | Poprawność docstringów |

**Ignorowane:** `E501` (kontrolowane przez formatter), `N802`/`N815` (projekt używa CamelCase), `N999`, `LOG015`.

**Komendy walidacji:**

```bash
ruff format --check
ruff check
pyright .
uv run pytest -m "not manual and not gpu and not benchmark" --cov -v
```
