# models/ — Modele danych

Modele danych niezwiązane bezpośrednio z silnikiem adnotacji ani UI. Przechowują struktury danych dla zewnętrznych integracji (np. klasyfikacja GPT).

---

## Struktura

```
models/
└── annotations_classified.py   # Sklasyfikowane adnotacje (bool)
```

---

## Moduły

### `annotations_classified.py` (123 linie)

**Dataclass `AnnotationsClassifiedBool`** — przechowuje wyniki binarnej klasyfikacji adnotacji (np. z GPT, zewnętrznego modelu).

**Pola (tablice NumPy):**

| Pole | Typ | Opis |
|---|---|---|
| `filenames` | `NDArray[np.str_]` | Nazwy plików |
| `class_ids` | `NDArray[np.int16]` | ID klas adnotacji |
| `x`, `y`, `w`, `h` | `NDArray[np.float32]` | Współrzędne bboxów (xywh) |
| `bools` | `NDArray[np.bool_]` | Wynik klasyfikacji (True/False) |

**Metody:**

| Metoda | Opis |
|---|---|
| `is_empty()` | Czy brak danych |
| `has_filename(filename)` | Czy plik istnieje w zbiorze |
| `filenames_unique` | Unikalne nazwy plików (property) |
| `get_filenames_where(result)` | Nazwy plików z danym wynikiem |
| `get_xywh_where(filename, result)` | Współrzędne bboxów z danym wynikiem dla pliku |
| `from_csv(path)` | Deserializacja z pliku CSV (staticmethod) |

**Zastosowanie:** przechowywanie wyników zewnętrznej klasyfikacji adnotacji (np. GPT oceniający poprawność labeli). Używana w `MainWindow.py` jako `gpt_annotations_classified`.
