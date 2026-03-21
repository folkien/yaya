# YAYA — Yet Another YOLO Annoter

## Przegląd

**YAYA** to desktopowa aplikacja (Python 3.11+ / PyQt5) służąca do tworzenia, edycji i walidacji adnotacji bounding-box w formacie YOLO.
Umożliwia zarówno ręczne rysowanie adnotacji, jak i automatyczną detekcję obiektów (YOLOv4 Darknet, YOLOv8 Ultralytics, YOLO World), porównywanie wyników detektora z adnotacjami ręcznymi (metryki TP/FP/FN, Precision, Recall) oraz analizę wizualną datasetu (HSV, rozmiary, duplikaty).

---

## Architektura wysokopoziomowa

```
┌─────────────────────────────────────────────────────────────────┐
│                      yolo-annotate.py                           │
│              (entry-point, argparse, boot)                      │
└───────┬─────────────────────┬───────────────────────────────────┘
        │                     │
        ▼                     ▼
 ┌──────────────┐    ┌────────────────┐
 │  Detectors/  │    │  engine/       │
 │ (detekcja)   │    │ (logika dom.)  │
 └──────┬───────┘    └───────┬────────┘
        │                    │
        │         ┌──────────┴──────────┐
        │         │                     │
        ▼         ▼                     ▼
 ┌─────────────────────┐    ┌────────────────────┐
 │   MainWindow.py     │    │   views/           │
 │   (kontroler GUI)   │    │   (widoki tabel)   │
 └──────┬──────────────┘    └────────────────────┘
        │
        ▼
 ┌─────────────────────────┐
 │  ViewerEditorImage.py   │
 │  (edytor obrazu Qt)     │
 └──────┬──────────────────┘
        │
        ▼
 ┌──────────────────────────────────────┐
 │  Gui/  +  helpers/                   │
 │  (rysowanie, kolory, widgety,        │
 │   pliki, boxy, metryki, NMS itp.)   │
 └──────────────────────────────────────┘
```

---

## Opis katalogów

### Katalog główny (`/`)

Pliki korzeniowe aplikacji:

| Plik | Opis |
|---|---|
| `yolo-annotate.py` | **Entry-point** — parsuje argumenty CLI, inicjalizuje detektor i annoter, uruchamia GUI. |
| `MainWindow.py` | Kontroler głównego okna (`MainWindowGui`). Łączy logikę biznesową (`Annoter`) z UI (`Ui_MainWindow`). Zarządza callbackami, nawigacją obrazów, tabelami, filtrami i sesją. |
| `MainWindow_ui.py` / `Ui_MainWindow.py` | Auto-generowany kod UI z pliku `MainWindow.ui` (Qt Designer). |
| `MainWindow.ui` | Definicja layoutu głównego okna w formacie Qt Designer XML. |
| `ViewerEditorImage.py` | Widget Qt (`QWidget`) służący jako interaktywny edytor obrazu — rysowanie / usuwanie / zmiana adnotacji myszką, zoom, panning, transformacje wizualne (threshold, sharpen, CLAHE, kontrast). |
| `config.example.toml` | Przykładowa konfiguracja — ustawienia detektora (confidence, NMS, strategia obrazu), Ultralytics, YOLO World prompt. |
| `pyproject.toml` | Konfiguracja projektu, zależności (`pyqt5`, `opencv-python-headless`, `ultralytics`, `numpy`, `pandas`, `imagehash`), narzędzia deweloperskie (`ruff`, `pyright`, `pytest`). |
| `tango_rc.py` | Skompilowany plik zasobów Qt (ikony Tango). |
| `install.sh` | Skrypt instalacyjny (zależności systemowe). |

---

### `engine/` — Logika biznesowa (rdzeń aplikacji)

Centralny pakiet z logiką domenową — brak zależności od Qt.

| Moduł | Opis |
|---|---|
| `annoter.py` | **Klasa `Annoter`** — rdzeń aplikacji. Zarządza listą plików w katalogu, sortowaniem, nawigacją (next/prev), detekcją obrazów, ładowaniem/zapisywaniem adnotacji i detekcji, ewaluacją metryk, filtrowaniem plików. Utrzymuje stan bieżącego pliku i powiązane dane (adnotacje, detekcje, visuals, metryki). |
| `annote.py` | **Klasa `Annote`** — model pojedynczej adnotacji bounding-box. Przechowuje: box (xywh znormalizowany), numer/nazwę klasy, confidence, typ autora (human/detector/hand), ewaluację (TP/FN), dane wizualne (HSV). Funkcje konwersji: `fromTxtAnnote()`, `fromDetection()`, `toTxtAnnote()`, `toYoloDetection()`. Globalna lista klas (`classNames`) inicjalizowana przez `Init()`. |
| `annote_enums.py` | Enumy: `AnnoteAuthorType` (byHuman / byDetector / byHand), `AnnoteEvaluation` (noEvaluation / TruePositiveLabel / TruePositive / FalseNegative), `AnnotatorType` (Default / ConfidenceHeat / Category). |
| `dataset.py` | **Klasa `Dataset`** — zarządzanie plikiem `dataset.txt` (lista ścieżek do plików adnotacji); metody `add()`, `remove()`, `load()`, `save()`, `is_inside()`. |
| `session.py` | **Klasa `Session`** — przechowuje timestamp sesji i pozwala kopiować bieżący plik (obraz + adnotacje + detekcje + visuals) do katalogu tymczasowego (`temp/session_*`). |
| `config_toml.py` | **Klasa `ConfigToml`** (Singleton) — czytnik konfiguracji TOML (`config.toml` → fallback `config.example.toml`). |
| `GuiClassKeycodes.py` | Mapowanie klawiszy klawiatury (`1-9, 0, -, =, backtick`) na numery klas YOLO z obsługą przesuwania offsetu (modifier backtick) dla >12 klas. |

#### `engine/annotators/` — Strategie rysowania adnotacji

Wzorzec Strategy — różne sposoby wizualizacji adnotacji na obrazie Qt:

| Moduł | Opis |
|---|---|
| `annotator.py` | **Klasa `Annotator`** — dispatcher; metoda `QtDraw()` deleguje rysowanie do odpowiedniej strategii na podstawie `AnnotatorType`. |
| `annotator_default.py` | `AnnotatorDefault` — domyślny styl: kolorowy prostokąt zależny od autora (human=czarny, detector=zielony, hand=ciemnozielony) i ewaluacji (FN=czerwony). |
| `annotator_confidence_heat.py` | `AnnotatorConfidenceHeat` — heatmapa kolorów R-Y-G (red→yellow→green) na podstawie confidence detektora. |
| `annotator_category.py` | `AnnotatorCategory` — kolorowanie adnotacji wg numeru klasy (cykliczna paleta matplotlib). |

---

### `Detectors/` — Warstwa detekcji obiektów

Abstrakcja nad różnymi backendami detekcji YOLO.

| Moduł | Opis |
|---|---|
| `__init__.py` | Fabryka detektorów: `ListDetectors()` — skanuje podkatalogi w poszukiwaniu plików `.cfg`+`.weights` (Darknet) lub `.pt` (Ultralytics); `CreateDetector()` — tworzy instancję detektora wg ID; `GetDetectorLabels()` — zwraca etykiety klas. |
| `DetectorYOLOv4.py` | Implementacja detektora YOLOv4 z biblioteką Darknet (`libdarknet.so`). |
| `detector_yolov4_cvdnn.py` | Implementacja detektora YOLOv4 przez OpenCV DNN backend (bez Darknet). |
| `detector_yolov8_ultralytics.py` | Implementacja detektora YOLOv5/v8/v11 z Ultralytics SDK (`.pt` modele). |

#### `Detectors/common/` — Interfejsy i typy wspólne

| Moduł | Opis |
|---|---|
| `Detector.py` | **Klasa bazowa `Detector`** — interfejs detekcji: `Init()`, `Detect(frame, confidence, nms_thresh, ...)` → lista detekcji; metoda `EnsembleBoxes()` z obsługą różnych metod NMS. Enum `NmsMethod` (Nms / SoftNms / NmWeighted / WeightedBoxFusion). |
| `Detection.py` | **Dataclass `Detection`** — surowa detekcja z YOLO HEAD: `xywh`, `objectness`, `probabilities`; properties: `confidence`, `class_id`, `class_label`, `center`, `area`. |
| `image_strategy.py` | **Enum `ImageStrategy`** — strategie przetwarzania obrazu przed detekcją: Rescale, RescaleNearest, LetterBox, Tiling2x2, Tiling (SAHI). |

#### `Detectors/yolov4/` — Binding Darknet

| Moduł | Opis |
|---|---|
| `darknet.py` | Python binding do biblioteki `libdarknet.so` (ctypes). |
| `test.py` | Prosty test detekcji Darknet. |

---

### `Gui/` — Warstwa prezentacji (widgety, rysowanie, kolory)

Narzędzia graficzne niezależne od logiki biznesowej.

| Moduł | Opis |
|---|---|
| `colors.py` | Stałe kolorów BGR (OpenCV): white, red, green, blue, itd. Schematy kolorów: `colorSchemeBright`, `colorSchemeMatplotlib`. Funkcje: `GetNextTableColor()`, `CreateColorsForLabels()` itp. |
| `drawing.py` | Funkcje rysowania OpenCV: `DrawDetections()`, `DrawText()`, `CreateColors()`. |

#### `Gui/widgets/` — Niestandardowe widgety tabelowe

Specjalizowane `QTableWidgetItem` dla różnych typów danych w tabelach:

| Widget | Typ danych |
|---|---|
| `ImageTableWidgetItem` | Miniaturka obrazu (z opcjonalnym cropem adnotacji) |
| `AnnotationsTableWidgetItem` | Lista klas adnotacji |
| `BoolTableWidgetItem` | Wartość bool z kolorowym tłem |
| `EvalTableWidgetItem` | Ewaluacja (TP/FP/FN) z kolorami |
| `FloatTableWidgetItem` | Liczba zmiennoprzecinkowa z sortowalnym formatem |
| `HsvTableWidgetItem` | Wartość HSV z kolorowym tłem |
| `ImhashTableWidgetItem` | Perceptual hash obrazu |
| `PercentTableWidgetItem` | Procent z paskiem kolorowym |
| `RectTableWidgetItem` | Wymiary prostokąta (width×height) |
| `StatTableWidgetItem` | Wartość statystyczna |

---

### `views/` — Widoki tabel (generowanie zawartości QTableWidget)

Klasy statyczne generujące zawartość tabel w UI z danych `Annoter`:

| Moduł | Opis |
|---|---|
| `ViewImagesTable.py` | Tabela główna — lista plików z kolumnami: nazwa, rozmiar, annotated, validation, correct, classes, detections, czas, HSV, metryki (IOU, precision, recall, errors). |
| `ViewAnnotations.py` | Tabela adnotacji — widok wszystkich adnotacji (human) z kolumnami: file/ID, kategoria, confidence, ewaluacja, rozmiar, ratio, area, HSV. |
| `ViewDetections.py` | Tabela detekcji — widok wszystkich detekcji (detector) z analogicznymi kolumnami. |
| `ViewFilters.py` | Generator przycisków filtrów (klasy, typy obrazów, detekcji) z `QButtonGroup`. |
| `ViewImagesSummary.py` | Podsumowanie — sumaryczne metryki (correct, precision, recall, new detections). Klasa `Summary` agreguje dane ze wszystkich plików. |

---

### `helpers/` — Biblioteka narzędzi pomocniczych

Moduły utility niezależne od GUI i logiki domenowej:

| Moduł | Opis |
|---|---|
| `boxes.py` | Operacje na bounding-boxach: konwersje (xywh↔xyxy, relative↔absolute, Bbox2Rect/Rect2Bbox), IOU, containment, overlap, tiling IOU, ekstrakcja fragmentów obrazu. Klasa `BoxState` (Isolated/Occluding/Contained/...). |
| `files.py` | Operacje plikowe: `GetFiles()`, `GetFilename()`, `ChangeExtension()`, `IsImageFile()`, `DeleteFile()`, `FixPath()`, `GetFileLocation()`, `GetNotExistingSha1Filepath()`. |
| `textAnnotations.py` | Odczyt/zapis adnotacji i detekcji: `ReadAnnotations()` / `SaveAnnotations()` (format: `class x y w h`); `ReadDetections()` / `SaveDetections()` (format: `class conf x y w h`). Format plików `.txt` (adnotacje) i `.detector` (detekcje). |
| `metrics.py` | **Dataclass `Metrics`** — metryki ewaluacji: TP/FP/TN/FN, LTP, IOU, precision, recall, detections, matches. Funkcja `EvaluateMetrics()` — porównuje adnotacje z detekcjami i oblicza statystyki. |
| `visuals.py` | **Dataclass `Visuals`** — właściwości wizualne obrazu: width, height, grid 20×20 (H, S, V), dhash, isDuplicate. Odczyt/zapis z pliku `.visuals.json`. Klasa `VisualsDuplicates` — wykrywanie duplikatów (perceptual hash). |
| `QtDrawing.py` | Prymitywy rysowania Qt: `CvImage2QtImage()`, `QDrawRectangle()`, `QDrawElipse()`, `QDrawTriangle()`, `QDrawCrosshair()`, `QDrawText()`, konwersje kolorów CV↔Qt. Enum `TextAlignment`. |
| `colors.py` | Stałe kolorów BGR, schematy kolorów, funkcje pomocnicze do generowania palet. |
| `prefilters.py` | Filtrowanie adnotacji po IOU i confidence (redukcja duplikatów detekcji). |
| `detections.py` | Scalanie detekcji z wielu kafelków (tiles) na podstawie IOU. |
| `ensemble_boxes_nms.py` | Implementacja NMS i Soft-NMS (CPU, float) na znormalizowanych boxach [0,1]. |
| `ensemble_boxes_nmw.py` | Non-Maximum Weighted (NMW) — ważony NMS. |
| `ensemble_boxes_wbf.py` | Weighted Boxes Fusion (WBF) — fuzja boxów z wielu modeli. |
| `soft_nms.py` | Alternatywna implementacja Soft-NMS. |
| `transformations.py` | Transformacje obrazu OpenCV: noise (gauss, S&P, poisson), blur, threshold, sharpen, CLAHE, kontrast, letterbox, tiling, resize, flip, rotate. |
| `images.py` | Skalowanie obrazu z zachowaniem proporcji: `ResizeToMaxWidth()`, `ResizeToHeight()`, `GetFixedFitToBox()`. |
| `hashing.py` | Generowanie losowych SHA-1 nazw plików; sprawdzanie czy nazwa jest SHA-1. |
| `algebra.py` | Geometria 2D: `GetDistance()`, `GetTranslation()`, `GetMiddlePoint()`, `EuclideanDistance()`. |
| `json.py` | Zapis/odczyt JSON z obsługą dataclass, datetime, set. Klasa `EnhancedJSONEncoder`. |
| `texts.py` | Funkcje tekstowe: `abbrev()` (skracanie tekstu). |
| `git.py` | Informacje z Git: `GetGitRev()`, `GetGitBranchRev()`, `GetYearWeekRev()`. |
| `gpu.py` | Sprawdzanie CUDA (`IsCuda()`), znajdowanie GPU z najmniejszym zużyciem pamięci. |
| `MarkdownReport.py` | Generator raportów Markdown: sekcje, tabele, obrazy, dataframe. Używany przez `DecoratorDistributionShowcase`. |
| `Singleton.py` | Metaklasa `Singleton` — wzorzec Singleton (używana przez `ConfigToml`). |
| `aisp_typing.py` | Aliasy typów (`NumpyArray` itp.). |

---

### `Decorators/` — Dekoratory analizy datasetu

| Moduł | Opis |
|---|---|
| `DecoratorDistributionShowcase.py` | Generuje raport dystrybucji klas w datasecie — wybiera reprezentatywne próbki z każdej kategorii, wycina subobrazki adnotacji, tworzy raport Markdown ze statystykami i miniaturkami. |

---

### `models/` — Modele danych

| Moduł | Opis |
|---|---|
| `annotations_classified.py` | **Dataclass `AnnotationsClassifiedBool`** — przechowuje wyniki klasyfikacji adnotacji (np. z GPT): tablice NumPy (filenames, class_ids, xywh, bools). Metody: `from_csv()`, zapytania `get_xywh_where()`, `get_filenames_where()`, `has_filename()`. |

---

### `yaya/` — Pakiet Python (pusty)

Pakiet top-level `yaya` — obecnie pusty (`__init__.py`). Rezerwacja dla przyszłej modularyzacji.

---

### `tests/` — Testy

| Plik | Opis |
|---|---|
| `test_boxes.py` | Testy operacji na bounding-boxach (`helpers/boxes.py`). |
| `test_benchmark_nms.py` | Benchmark wydajnościowy metod NMS. |
| `test_gpu.py` | Testy dostępności GPU/CUDA. |
| `test_yolo_world.py` | Test integracyjny YOLO World. |
| `yolo_world/` | Podkatalog z danymi testowymi dla YOLO World. |

---

### `icons/` — Zasoby ikon (Tango)

Zestaw ikon w stylu Tango (16×16, 22×22, 32×32) dla interfejsu Qt. Plik `tango.qrc` definiuje zasoby, skompilowane do `tango_rc.py`.

---

### `scripts/`

| Plik | Opis |
|---|---|
| `yolo-annotate.sh` | Skrypt shellowy do uruchamiania aplikacji. |

---

### `input/` — Przykładowe dane wejściowe

Katalog z przykładowymi obrazami do testowania aplikacji.

---

### `temp/` — Pliki tymczasowe

Katalog na dane sesji (`session_*`), pliki tymczasowe.

---

### `doc/` — Dokumentacja

Katalog z dokumentacją techniczną projektu (ten plik).

---

## Przepływ danych (Data Flow)

```
1. Start: yolo-annotate.py
   │
   ├─ Parsowanie argumentów (--input, --detector, --noDetector, ...)
   ├─ ListDetectors() → skanowanie Detectors/ pod .cfg/.pt
   ├─ CreateDetector() → inicjalizacja detektora (Darknet/Ultralytics)
   ├─ annote.Init(classNames) → załadowanie nazw klas
   │
   ├─ Annoter(filepath, detector, ...) → załadowanie katalogu plików
   │     ├─ Skanowanie plików obrazów w katalogu
   │     ├─ Dla każdego pliku:
   │     │     ├─ ReadAnnotations() → .txt (adnotacje YOLO: class x y w h)
   │     │     ├─ ReadDetections() → .detector (detekcje: class conf x y w h)
   │     │     ├─ Visuals.Load() → .visuals.json (cache HSV/hash)
   │     │     └─ EvaluateMetrics() → porównanie adnotacji z detekcjami
   │     └─ Dataset.load() → dataset.txt (lista plików w datasecie)
   │
   └─ MainWindowGui(args, detector, annoter)
         ├─ QApplication + Ui_MainWindow (z MainWindow.ui)
         ├─ ViewerEditorImage (widget edytora obrazu)
         ├─ Views: ViewImagesTable, ViewAnnotations, ViewDetections,
         │         ViewFilters, ViewImagesSummary
         └─ gui.Run() → główna pętla Qt
```

### Format plików danych

Dla każdego obrazu `image.jpg` mogą istnieć towarzyszące pliki:

| Plik | Format | Opis |
|---|---|---|
| `image.txt` | `class_id x_center y_center width height` | Adnotacje YOLO (współrzędne znormalizowane 0–1) |
| `image.detector` | `class_name confidence x_center y_center width height` | Wyniki detekcji (cache) |
| `image.visuals.json` | JSON | Cache właściwości wizualnych (HSV grid, hash, wymiary) |
| `dataset.txt` | Lista ścieżek (1 na linię) | Plik datasetu — które pliki są w zbiorze treningowym |

---

## Konfiguracja (`config.toml`)

```toml
[detector]
detector = "Default"          # Default | YoloWorld
confidence = 0.25             # Próg confidence
nms = 0.45                    # Próg NMS
nms_method = "greedy"         # Nms | SoftNms | NmWeighted | WeightedBoxFusion
image_strategy = "resize"     # Rescale | LetterBox | Tiling2x2 | Tiling (SAHI)

[detector.ultralytics]
force_cpu = false
task = "detect"               # detect | segment | classify
half_precision = true
use_tensorrt = false

[detector.yolo_world]
default_prompt = "warning lamp:lamp1, emergency light:lamp2"
```

---

## Klawisze skrótów

| Klawisz | Akcja |
|---|---|
| `LPM` (lewy przycisk myszy) | Tworzenie adnotacji (rysowanie bounding-box) |
| `PPM` (prawy przycisk myszy) | Usuwanie adnotacji |
| `d` | Uruchomienie detektora na bieżącym obrazie |
| `r` | Usunięcie zaznaczonej adnotacji |
| `c` | Usunięcie wszystkich adnotacji |
| `s` | Zapis (jeśli brak błędów) |
| `→` lub `.` | Następny obraz |
| `←` lub `,` | Poprzedni obraz |
| `1-9, 0, -, =` | Wybór klasy (0–11) |
| `` ` `` (backtick) | Przesunięcie offsetu klas (+12) |

---

## Uruchamianie

```bash
# Instalacja zależności
uv sync

# Uruchomienie z katalogiem wejściowym
python yolo-annotate.py -i input/

# Uruchomienie z detektorem #0
python yolo-annotate.py -i input/ -det 0

# Uruchomienie bez detektora
python yolo-annotate.py -i input/ -nd

# Wymuszone przeliczenie detekcji (usuwa stare .detector)
python yolo-annotate.py -i input/ -f
```

### Argumenty CLI

| Argument | Opis | Domyślnie |
|---|---|---|
| `-i, --input` | Ścieżka do katalogu z obrazami | — |
| `-c, --config` | Ścieżka do pliku konfiguracji | `config.toml` |
| `-det, --detector` | ID detektora (index) | `0` |
| `-detc, --detectorConfidence` | Próg confidence detektora | `0.4` |
| `-detnms, --detectorNms` | Próg NMS detektora | `0.45` |
| `-nd, --noDetector` | Wyłączenie detektora | `false` |
| `-oe, --onlyFilesWithErrors` | Tylko pliki z błędami | `false` |
| `-f, --forceDetector` | Wymuszenie detekcji (usunięcie cache) | `false` |
| `-v, --verbose` | Tryb verbose | `false` |

---

## Dodawanie detektora

1. W katalogu `Detectors/` utwórz podkatalog (np. `yolov8custom/`).
2. **Darknet**: wrzuć pliki `yolo.cfg`, `yolo.weights`, `yolo.data`, `yolo.names`.
3. **Ultralytics**: wrzuć plik `model.pt` i `model.names`.
4. Detektor zostanie automatycznie wykryty przy uruchomieniu.

---

## Stack technologiczny

| Składnik | Technologia |
|---|---|
| Język | Python 3.11+ |
| GUI | PyQt5 5.15 |
| Obraz / CV | OpenCV (headless) |
| Detekcja | Ultralytics (YOLOv5/v8/v11), Darknet (YOLOv4) |
| Dane | NumPy, Pandas |
| Hash obrazów | imagehash (perceptual hash) |
| Konfiguracja | TOML (tomllib / tomli) |
| Testy | pytest, pytest-cov |
| Lint / Format | ruff |
| Typy | pyright (strict) |
| Pakiety | uv (resolver/lockfile) |
