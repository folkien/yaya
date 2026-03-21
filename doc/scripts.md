# scripts/ — Skrypty uruchomieniowe

Skrypty shellowe ułatwiające uruchamianie aplikacji.

---

## Struktura

```
scripts/
└── yolo-annotate.sh   # Skrypt uruchomieniowy
```

---

## Pliki

### `yolo-annotate.sh`

Skrypt Bash uruchamiający aplikację YAYA:

1. Rozwiązuje dowiązania symboliczne (readlink) do znalezienia rzeczywistego katalogu skryptu
2. Przechodzi do katalogu nadrzędnego (root projektu)
3. Uruchamia `./yolo-annotate.py` z przekazanymi argumentami

Przydatny gdy aplikacja jest zainstalowana przez symlink w `$PATH` — skrypt automatycznie znajduje właściwy katalog roboczy.

**Użycie:**

```bash
./scripts/yolo-annotate.sh -i /path/to/images/
```
