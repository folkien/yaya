# tests/ — Testy

Testy jednostkowe, integracyjne i benchmarkowe. Framework: `pytest`.

---

## Struktura

```
tests/
├── test_benchmark_nms.py    # Benchmark metod NMS
├── test_boxes.py            # Testy operacji na bounding-boxach
├── test_gpu.py              # Testy dostępności GPU/CUDA
├── test_yolo_world.py       # Test integracyjny YOLO World
└── yolo_world/              # Dane testowe dla YOLO World
```

---

## Pliki testowe

### `test_boxes.py`

Testy jednostkowe dla `helpers.boxes.tiles_iou`:

- **`test_tiles_iou()`** — weryfikacja IOU dla identycznych, sąsiadujących i oddzielnych kafelków o różnych rozmiarach
- **`test_tiles_sim()`** — testy podobieństwa kafelków

Testowane scenariusze:
- Identyczne boxy → IOU = 1.0
- Sąsiadujące boxy bez nakładania → IOU = 0.0
- Częściowe nakładanie → IOU ∈ (0, 1)
- Różne rozmiary kafelków

### `test_benchmark_nms.py` (92 linie)

Benchmark wydajnościowy metod NMS:

- `DetectionsCreate()` — generuje losowe detekcje (boxy + confidence + labels)
- `EnsembleBoxes()` — testuje wszystkie 4 metody: NMS, Soft-NMS, NMW, WBF
- Mierzy czas wykonania każdej metody
- Marker: `benchmark`

### `test_gpu.py`

Test dostępności GPU:

- `test_lowest_gpu()` — sprawdza `CudaDeviceLowestMemory()`
- Pomija (`pytest.skip`) jeśli CUDA niedostępna
- Marker: `gpu`

### `test_yolo_world.py`

Test integracyjny YOLO World (open-vocabulary detection):

- Ładuje obraz testowy z `tests/yolo_world/`
- Testuje detekcję klas tekstowych ("person", "bus", "shop")
- Wymaga biblioteki `inference.models.yolo_world`
- Marker: `manual`

---

## Uruchamianie

```bash
# Wszystkie testy (bez manual/gpu/benchmark)
uv run pytest -m "not manual and not gpu and not benchmark" -v

# Tylko testy boxów
uv run pytest tests/test_boxes.py -v

# Benchmark NMS
uv run pytest tests/test_benchmark_nms.py -v

# Testy GPU (wymaga CUDA)
uv run pytest tests/test_gpu.py -v
```
