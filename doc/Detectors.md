# Detectors/ — Warstwa detekcji obiektów YOLO

Abstrakcja nad różnymi backendami detekcji YOLO. Wspiera dynamiczne wykrywanie dostępnych modeli, fabrykę detektorów i wiele metod NMS (Non-Maximum Suppression).

---

## Struktura

```
Detectors/
├── __init__.py                    # Fabryka detektorów + skanowanie modeli
├── DetectorYOLOv4.py              # Detektor YOLOv4 (natywny Darknet)
├── detector_yolov4_cvdnn.py       # Detektor YOLOv4 (OpenCV DNN)
├── detector_yolov8_ultralytics.py # Detektor YOLOv5/v8/v11 (Ultralytics)
├── common/                        # Interfejsy i typy wspólne
│   ├── __init__.py
│   ├── Detector.py                # Klasa bazowa Detector + enum NmsMethod
│   ├── Detection.py               # Dataclass detekcji (YOLO HEAD)
│   └── image_strategy.py          # Enum strategii obrazu
└── yolov4/                        # Binding natywnego Darknet
    ├── darknet.py                 # ctypes wrapper libdarknet.so
    └── test.py                    # Test Darknet
```

---

## Fabryka detektorów (`__init__.py`)

### `ListDetectors(path=None) → list[tuple]`

Skanuje podkatalogi `Detectors/` (lub podanej ścieżki) w poszukiwaniu modeli:

- **Darknet:** pliki `.cfg` + `.weights` + `.data` + `.names`
- **Ultralytics:** pliki `.pt` + `.names`

Zwraca listę krotek `(DetectorType, cfg, weights, meta, names)`.

### `CreateDetector(detectorID, gpuID=0, path=None) → Detector | None`

Tworzy instancję detektora na podstawie indeksu z `ListDetectors()`:

- `DetectorType.Ultralytics` → `DetectorYolov8`
- `DetectorType.Darknet` / `DetectorType.CVDNN` → `DetectorYOLOv4` lub `DetectorCVDNN`

### `GetDetectorLabels(detectorID) → list[str]`

Zwraca nazwy klas z pliku `.names` bez inicjalizacji detektora.

### `IsDarknet() → bool`

Sprawdza czy biblioteka `/usr/local/lib/libdarknet.so` istnieje w systemie.

### Enum `DetectorType`

| Wartość | Opis |
|---|---|
| `Darknet` | Natywna biblioteka Darknet (ctypes) |
| `CVDNN` | OpenCV DNN backend |
| `Ultralytics` | Ultralytics SDK (YOLOv5/v8/v11) |

---

## Implementacje detektorów

### `DetectorYOLOv4` (natywny Darknet) — 490 linii

Implementacja korzystająca z `libdarknet.so` (C library):

- Ładowanie modelu z `.cfg` / `.weights` / `.names`
- Zarządzanie pamięcią GPU (inicjalizacja/destrukcja)
- Obsługa strategii tilingowej (`ImageTile` NamedTuple)
- Wymaga kompilacji i instalacji Darknet w systemie

### `DetectorCVDNN` (OpenCV DNN) — 225 linii

Alternatywa bez natywnego Darknet — czysty OpenCV:

- Ładowanie przez `cv2.dnn.readNetFromDarknet(cfg, weights)`
- Działa na CPU i GPU OpenCV (CUDA backend)
- Funkcja `xlylwh_to_xyxy()` konwertuje format wyjściowy
- Nie wymaga kompilacji dodatkowych bibliotek

### `DetectorYolov8` (Ultralytics) — 300 linii

Główny współczesny detektor — Ultralytics SDK:

- Obsługuje modele `.pt` (YOLOv5/v8/v11)
- Konfiguracja z TOML: confidence, NMS, task (detect/segment/classify), half precision
- Opcjonalny eksport i inferencing z TensorRT
- Wymuszanie CPU (`force_cpu = true`)

---

## Podkatalog `common/` — Interfejsy i typy wspólne

### `Detector` — klasa bazowa (160 linii)

Interfejs dla wszystkich detektorów:

| Metoda | Opis |
|---|---|
| `Init()` | Inicjalizacja po utworzeniu |
| `Detect(frame, confidence, nms_thresh, ...)` | Detekcja obiektów → lista `(label, confidence, box)` |
| `Close()` | Zamknięcie i zwolnienie zasobów |
| `GetDetector()` | Zwraca siebie |
| `GetClassNames()` | Lista nazw klas |
| `EnsembleBoxes(boxes, ...)` | Filtrowanie NMS z wyborem metody |

Enum `NmsMethod`:

| Wartość | Algorytm |
|---|---|
| `Nms` | Klasyczny Non-Maximum Suppression |
| `SoftNms` | Soft-NMS (wygładzanie confidence) |
| `NmWeighted` | Non-Maximum Weighted (uśrednianie boxów) |
| `WeightedBoxFusion` | Weighted Boxes Fusion (ensemble) |

### `Detection` — dataclass

Surowa detekcja z YOLO HEAD:

| Pole | Typ | Opis |
|---|---|---|
| `xywh` | `list[float]` | Bounding-box (center_x, center_y, width, height) |
| `objectness` | `float` | Wartość objectness |
| `probabilities` | `list[float]` | Prawdopodobieństwa per klasa |

Properties: `confidence` (max prob), `class_id`, `class_label`, `center`, `width`, `height`, `area`.

### `ImageStrategy` — enum

Strategie przygotowania obrazu do detekcji:

| Wartość | Opis |
|---|---|
| `Rescale` | Skalowanie do rozmiaru wejściowego sieci |
| `RescaleNearest` | Skalowanie nearest-neighbor |
| `LetterBox` | Letterbox (padding zachowujący proporcje) |
| `Tiling2x2` | Podział na 4 kafelki 2×2 |
| `Tiling` | Podział na kafelki (SAHI-style) |

---

## Podkatalog `yolov4/` — Binding Darknet

### `darknet.py` (376 linii)

Python wrapper (ctypes) dla natywnej biblioteki Darknet C:

- Struktury ctypes: `BOX`, `DETECTION`, `DETNUMPAIR`, `IMAGE`
- Dynamiczne ładowanie `libdarknet.so` / `.dll`
- Wywołania FFI: `load_network`, `detect_image`, `free_detections`

---

## Dodawanie nowego detektora

1. W katalogu `Detectors/` utwórz podkatalog (np. `my_model/`)
2. Dla **Darknet**: umieść `yolo.cfg`, `yolo.weights`, `yolo.data`, `yolo.names`
3. Dla **Ultralytics**: umieść `model.pt` i `model.names`
4. Detektor zostanie automatycznie wykryty przez `ListDetectors()` przy starcie
