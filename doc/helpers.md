# helpers/ — Biblioteka narzędzi pomocniczych

Moduły utility niezależne od GUI i logiki domenowej. Stanowią fundament operacji na bounding-boxach, plikach, metrykach, obrazach i rysowaniu Qt. Większość modułów nie importuje PyQt5 — wyjątkiem jest `QtDrawing.py`.

---

## Struktura

```
helpers/
├── __init__.py
├── aisp_typing.py           # Aliasy typów (NumpyArray)
├── algebra.py               # Geometria 2D (odległość, translacja, kąty)
├── boxes.py                 # Operacje na bounding-boxach (konwersje, IOU)
├── colors.py                # Stałe kolorów BGR + schematy
├── detections.py            # Scalanie detekcji z kafelków (tiles)
├── ensemble_boxes_nms.py    # NMS + Soft-NMS (ZFTurbo)
├── ensemble_boxes_nmw.py    # Non-Maximum Weighted (NMW)
├── ensemble_boxes_wbf.py    # Weighted Boxes Fusion (WBF)
├── files.py                 # Operacje plikowe (ścieżki, rozszerzenia)
├── git.py                   # Informacje z Git (tag, branch, hash)
├── gpu.py                   # Detekcja CUDA/GPU, info o systemie
├── hashing.py               # SHA-1 nazwy plików
├── images.py                # Skalowanie obrazów z proporcjami
├── json.py                  # JSON z obsługą dataclass/datetime
├── MarkdownReport.py        # Generator raportów Markdown
├── metrics.py               # Metryki ewaluacji (TP/FP/FN/Precision/Recall)
├── prefilters.py            # Filtr IOU+confidence (pre-NMS)
├── QtDrawing.py             # Prymitywy rysowania Qt (QPainter)
├── Singleton.py             # Metaklasa Singleton
├── soft_nms.py              # Soft-NMS (alternatywna implementacja)
├── textAnnotations.py       # Odczyt/zapis plików adnotacji YOLO (.txt)
├── texts.py                 # Funkcje tekstowe (abbrev)
├── transformations.py       # Transformacje obrazu (augmentacja)
└── visuals.py               # Właściwości wizualne obrazu (HSV, hash)
```

---

## Moduły — Bounding-boxy i NMS

### `boxes.py` (384 linie)

Fundamentalny moduł operacji na bounding-boxach:

| Grupa | Funkcje |
|---|---|
| **Konwersje** | `Bbox2Rect()`, `Rect2Bbox()`, `to_xyxy()`, `ToAbsolute()`, `ToRelative()`, `PointToAbsolute()`, `PointToRelative()` |
| **IOU** | `iou()`, `tiles_iou()`, `intersection()` |
| **Geometrie** | `IsInside()`, `GetContainingBox()`, `ExtractBoxImagePart()`, `GetCenterPoint()` |
| **Klasa `BoxState`** | Stan okluzji: Isolated, Occluding, Occluded, Containing, Contained |

Formaty bounding-boxów:
- **YOLO (Bbox):** `(center_x, center_y, width, height)` — znormalizowane 0–1
- **Rect (xyxy):** `(x1, y1, x2, y2)` — znormalizowane 0–1
- **Absolute:** `(x1, y1, x2, y2)` — piksele

### `ensemble_boxes_nms.py` (259 linii)

Implementacja klasycznego NMS i Soft-NMS autorstwa ZFTurbo:

- Normalizacja boxów do zakresu [0, 1]
- Walidacja (usunięcie boxów o zerowej powierzchni)
- Trzy metody: linear soft-NMS, gaussian soft-NMS, standard NMS

### `ensemble_boxes_nmw.py` (177 linii)

Non-Maximum Weighted (NMW) — wariant NMS:

- Zamiast usuwać boxy, uśrednia nakładające się detekcje
- Bazuje na artykule "CAD: Scale Invariant Framework"

### `ensemble_boxes_wbf.py` (180 linii)

Weighted Boxes Fusion (WBF) — ensemble detekcji:

- Łączy boxy z wielu modeli w ważone kombinacje
- Zaawansowana alternatywa dla NMS w scenariuszach multi-model
- Autorstwa ZFTurbo

### `soft_nms.py` (122 linie)

Alternatywna implementacja Soft-NMS (CPU, czysta Python):

- Artykuł: "Improving Object Detection With One Line of Code"
- Metody: liniowa, gaussowska, oryginalna NMS

### `prefilters.py`

Filtr pre-NMS adnotacji:

- `filter_iou_by_confidence(annotations1, annotations2, maxIOU)` — dla par adnotacji o IOU ≥ próg, zachowuje tę z wyższą confidence

### `detections.py`

Scalanie detekcji z kafelków (tiles):

- `tiles_detections_merge(tiles_detections, iou_threshold)` — łączy nakładające się detekcje z różnych kafelków, tworzy bounding-box zawierający

---

## Moduły — Pliki i adnotacje

### `files.py` (111 linii)

Operacje na ścieżkach plików:

| Funkcja | Opis |
|---|---|
| `GetFiles(base, pattern)` | Lista plików wg wzorca (fnmatch) |
| `GetFilename(path)` | Ścieżka bez rozszerzenia |
| `GetExtension(path)` | Rozszerzenie pliku |
| `ChangeExtension(path, ext)` | Zmiana rozszerzenia |
| `IsImageFile(filepath)` | Czy plik to obraz (.png/.jpg/.jpeg/.gif/.tiff) |
| `DeleteFile(path)` | Usunięcie pliku z logowaniem |
| `FixPath(path)` | Normalizacja ścieżki (trailing slash) |
| `GetFileLocation(path)` | Katalog pliku |
| `CreateDirectory(path)` | Tworzenie katalogu (recursive) |
| `GetNotExistingSha1Filepath()` | Unikalna nazwa SHA-1 w katalogu |
| `RenameToSha1Filepath()` | Zmiana nazwy pliku na SHA-1 |

### `textAnnotations.py`

Odczyt/zapis plików adnotacji YOLO:

| Funkcja | Format pliku | Opis |
|---|---|---|
| `ReadAnnotations(imagePath, ext='.txt')` | `class_id x y w h` | Odczyt adnotacji |
| `SaveAnnotations(imagePath, annotations)` | `class_id x y w h` | Zapis adnotacji |
| `ReadDetections(imagePath, ext='.txt')` | `class_name conf x y w h` | Odczyt detekcji |
| `SaveDetections(imagePath, annotations)` | `class_name conf x y w h` | Zapis detekcji |
| `DeleteAnnotations(imagePath)` | — | Usunięcie pliku adnotacji |
| `IsExistsAnnotations(imagePath)` | — | Sprawdzenie istnienia |
| `GetImageFilepath(annotationPath)` | — | Znalezienie obrazu dla adnotacji |

---

## Moduły — Metryki i wizualne

### `metrics.py` (325 linii)

Metryki ewaluacji detekcji:

**Dataclass `Metrics`:**

| Pole | Opis |
|---|---|
| `TP`, `FP`, `TN`, `FN` | True/False Positive/Negative |
| `LTP` | Label True Positive (klasa + box poprawne) |
| `iou_avg` | Średnie IOU |
| `overlapping_iou` | IOU nakładania |
| `detections` | Lista detekcji |
| `new_detections` | Nowe detekcje (bez dopasowania) |
| `matches` | Lista par (adnotacja, detekcja) |

Properties: `precision`, `recall`, `correct`, `correct_bboxes`, `detections_confidence`, `matches_confidence`.

**Funkcja `EvaluateMetrics(annotations, detections)`** — porównuje adnotacje z detekcjami, matchuje boxy wg IOU, wylicza metryki.

### `visuals.py` (198 linii)

Właściwości wizualne obrazu:

**Dataclass `Visuals`:**

| Pole | Opis |
|---|---|
| `imagepath` | Ścieżka do obrazu |
| `width`, `height` | Wymiary |
| `grid` | Siatka 20×20 tupli `(H, S, V)` |
| `dhash` | Perceptualny hash (differential hash) |
| `isDuplicate` | Flaga duplikatu |

Properties: `hue`, `saturation`, `brightness` (średnie z gridu), `numpy_grid`.

Serializacja do/z pliku `.visuals.json`. Klasa `VisualsDuplicates` — wykrywanie duplikatów wg dhash i progu Hamminga.

---

## Moduły — Rysowanie Qt

### `QtDrawing.py` (449 linii)

Most pomiędzy OpenCV a PyQt5:

| Funkcja | Opis |
|---|---|
| `CvImage2QtImage(cvImg)` | Konwersja `np.ndarray` → `QPixmap` |
| `CvBGRColorToQColor(color)` | BGR tuple → `QColor` |
| `QDrawRectangle(painter, points, ...)` | Prostokąt z pędzlem i opacity |
| `QDrawElipse(painter, point, ...)` | Elipsa/kółko |
| `QDrawTriangle(painter, point, ...)` | Trójkąt (znacznik) |
| `QDrawCrosshair(painter, point, ...)` | Celownik |
| `QDrawText(painter, point, text, ...)` | Tekst z tłem i wyrównaniem |
| `CreateTraingle(x, y, size, angle)` | Polygon trójkąta (`QPolygon`) |

Enum `TextAlignment`: Center, TopRight, TopLeft, BottomRight, BottomLeft.

---

## Moduły — Obrazy i transformacje

### `images.py` (70 linii)

Skalowanie obrazów z zachowaniem proporcji:

| Funkcja | Opis |
|---|---|
| `ResizeToMaxWidth(image, maxWidth)` | Skaluj do max szerokości |
| `ResizeToHeight(image, maxHeight)` | Skaluj do max wysokości |
| `GetFixedFitToBox(w, h, boxW, boxH)` | Oblicz wymiary fitujące do prostokąta |

### `transformations.py` (390 linii)

Augmentacje obrazów OpenCV:

- **Szum:** gauss, salt & pepper, poisson, speckle
- **Filtry:** blur, sharpen, threshold, CLAHE, kontrast
- **Geometria:** letterbox, tiling, resize, flip, rotate
- **Wzorki:** AddPattern (siatka punktów)

---

## Moduły — Narzędzia ogólne

### `algebra.py` (48 linii)

Geometria 2D:

| Funkcja | Opis |
|---|---|
| `GetDistance(p1, p2)` | Odległość euklidesowa |
| `EuclideanDistance(p1, p2)` | j.w. (nowsza wersja) |
| `GetTranslation(p1, p2)` | Wektor translacji |
| `GetMiddlePoint(p1, p2)` | Punkt środkowy |
| `RadiansToDegree(rad)` | Konwersja kątów |
| `GetHypotenuse(a, b)` | Przeciwprostokątna |

### `json.py` (75 linii)

Serializacja JSON z obsługą dataclass/datetime/set:

- `EnhancedJSONEncoder` — encoder obsługujący `dataclass`, `datetime`, `timedelta`, `set`
- `jsonRead(filename)`, `jsonWrite(filename, data)`, `jsonShow(data)`, `jsonToStr(data)`, `jsonFromStr(raw)`

### `colors.py` (157 linii)

Stałe kolorów BGR i schematy — identyczne jak `Gui/colors.py`. Używany przez moduły `engine/` i `helpers/` bez importowania pakietu `Gui`.

### `hashing.py`

- `GetRandomSha1()` — unikalne SHA-1 z licznika + timestamp
- `IsSha1Name(name)` — walidacja 40-znakowego hex SHA-1

### `git.py`

- `GetGitRev()` — tag Git
- `GetGitBranchRev()` — tag + branch (fix dla slashy)
- `GetYearWeekRev()` / `GetYearWeekTimeRev()` — rewizja w formacie `YYWWvD`

### `gpu.py` (72 linie)

- `IsCuda()` — sprawdza `nvcc --version`
- `CudaDeviceLowestMemory()` — GPU z najmniejszym zużyciem pamięci (nvidia-smi)
- `GetOsDescription()`, `GetHostname()` — info o systemie

### `MarkdownReport.py` (140 linii)

Generator raportów Markdown:

- Nagłówek z Git tag/branch
- Sekcje, podsekcje, tekst, obrazy, listy
- Wstawianie DataFrame jako tabela MD
- Przyrostowy zapis do pliku

### `texts.py`

- `abbrev(text, length=50)` — skrócenie tekstu z `...`

### `Singleton.py`

Metaklasa `Singleton` — gwarantuje jedną instancję klasy (używana przez `ConfigToml`).

### `aisp_typing.py`

Alias `NumpyArray = np.ndarray` dla czytelności type-hints.
