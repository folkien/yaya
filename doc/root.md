# Pliki korzeniowe (katalog główny)

Pliki w katalogu głównym projektu — entry-point, kontroler GUI, edytor obrazu, konfiguracja projektu.

---

## Pliki źródłowe

### `yolo-annotate.py` — Entry-point aplikacji

Punkt wejścia programu. Sekwencja startu:

1. **Parsowanie argumentów CLI** (argparse): `--input`, `--detector`, `--detectorConfidence`, `--detectorNms`, `--noDetector`, `--forceDetector`, `--verbose`
2. **Konfiguracja logowania** (debug/info wg flagi `__debug__`)
3. **Inicjalizacja detektora:**
   - `ListDetectors()` — skanowanie dostępnych modeli
   - `CreateDetector()` → `detector.Init()` → `annote.Init(classNames)`
   - Fallback: jeśli brak detektorów → wyłączenie detekcji
4. **Normalizacja ścieżki wejściowej** (`FixPath`, `GetFileLocation`)
5. **Czyszczenie cache** (przy `--forceDetector`): usunięcie plików `.detector` i `.json`
6. **Tworzenie `Annoter`** z konfiguracją detektora
7. **Uruchomienie GUI** (`MainWindowGui.Run()`)

---

### `MainWindow.py` — Kontroler głównego okna (1006 linii)

Klasa `MainWindowGui` (dziedziczy `Ui_MainWindow`) — centralny kontroler GUI:

**Zarządza:**
- **Annoter** (`self.annoter`) — silnik adnotacji
- **ViewerEditorImage** — widget edytora obrazu
- **Widoki tabel:** `ViewImagesTable`, `ViewAnnotations`, `ViewDetections`, `ViewFilters`, `ViewImagesSummary`
- **Sesja** (`self.session`) — snapshot plików
- **Klasyfikacja GPT** (`self.gpt_annotations_classified`)
- **Ustawienia użytkownika** (`QSettings`) — ostatnio otwarta lokacja

**Kluczowe metody:**
- `LocationOpen(path)` — otwiera katalog z obrazami
- `SetupCallbacks()` — podpięcie sygnałów Qt do metod
- `SetupDefault()` — domyślne wartości UI
- `OpenedDirectoriesStore/Get()` — historia otwartych katalogów
- `ImageIDToRowNumber()` / `RowNumberToImageID()` — mapowanie tabel↔plików
- Callbacki: nawigacja, detekcja, zapis, eksport, transformacje, filtry

---

### `ViewerEditorImage.py` — Widget edytora obrazu (775 linii)

Klasa `ViewerEditorImage` (dziedziczy `QWidget`) — interaktywny edytor bounding-boxów:

**Tryby edycji:**
- `ModeAddAnnotation` — rysowanie nowej adnotacji (LPM)
- `ModeRemoveAnnotation` — usuwanie adnotacji (PPM)
- `ModeRenameAnnotation` — zmiana klasy
- `ModePaintCircle` — malowanie kółkiem

**Funkcje:**
- Zoom dynamiczny (scroll) z panningiem (środkowy przycisk)
- Miniaturka (lewy/prawy róg)
- Skalowanie: Resize, AspectRatio, OriginalSize, DynamicZoom
- Algorytm skalowania: Linear, Nearest
- Transformacje wizualne: threshold, sharpen, CLAHE, kontrast
- Delegowanie rysowania adnotacji do `Annotator` (wzorzec Strategy)
- Śledzenie trajektorii myszy dla rysowania bboxów

Enum `MouseButton`: NoButton, LMB, RMB, MMB, ScrollUp, ScrollDown.

---

### `MainWindow_ui.py` / `Ui_MainWindow.py`

Auto-generowany kod UI z pliku `MainWindow.ui` (Qt Designer). Definiuje layout okna głównego: toolbary, tabele, widgety, menu.

**Nie edytować ręcznie** — generowany przez `pyuic5`:

```bash
pyuic5 MainWindow.ui -o MainWindow_ui.py
```

### `MainWindow.ui`

Definicja layoutu głównego okna w formacie XML Qt Designer. Edycja wizualna w Qt Designer.

---

## Pliki konfiguracyjne

### `config.example.toml`

Przykładowa konfiguracja:

```toml
[detector]
detector = "Default"        # Default | YoloWorld
confidence = 0.25           # Próg confidence
nms = 0.45                  # Próg NMS
nms_method = "greedy"       # Nms | SoftNms | NmWeighted | WeightedBoxFusion
image_strategy = "resize"   # Rescale | LetterBox | Tiling2x2 | Tiling

[detector.ultralytics]
force_cpu = false
task = "detect"
half_precision = true
use_tensorrt = false

[detector.yolo_world]
default_prompt = "warning lamp:lamp1, emergency light:lamp2"
```

### `pyproject.toml`

Konfiguracja projektu:
- **Zależności runtime:** pyqt5, opencv-python-headless, numpy, pandas, ultralytics, imagehash, tqdm
- **Zależności dev:** ruff, pyright, pytest, pytest-cov, isort, pyqt5-stubs
- **Pyright:** strict mode
- **Build system:** pdm-backend

---

## Pliki zasobów

| Plik | Opis |
|---|---|
| `tango_rc.py` | Skompilowany plik zasobów Qt (ikony Tango) |
| `install.sh` | Skrypt instalacyjny (zależności systemowe) |
| `LICENSE` | Licencja projektu |
| `YoloAnnotateQtGui.py` | Plik projektu Qt |
| `YoloAnnotateQtGui.pyproject` | Konfiguracja projektu Qt Designer |
